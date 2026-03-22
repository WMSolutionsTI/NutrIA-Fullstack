from datetime import UTC, datetime
import json

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.v1.auth import get_password_hash
from app.api.v1.auth import get_current_user
from app.db import get_db
from app.domain.models.chatwoot_account import ChatwootAccount
from app.domain.models.nutricionista import Nutricionista
from app.domain.models.plano import Plano
from app.domain.models.tenant import Tenant
from app.workers.cadastro_assinatura_worker import (
    enviar_email_boas_vindas_assinatura,
    gerar_senha_temporaria,
    provisionar_conta_chatwoot,
)

router = APIRouter(prefix="/onboarding", tags=["Onboarding"])


class ConfirmarAssinaturaRequest(BaseModel):
    pagamento_id: str
    nome: str = Field(min_length=2)
    email: str
    plano_nome: str
    documento: str | None = None
    telefone: str | None = None


class SolicitarTrialRequest(BaseModel):
    nome: str = Field(min_length=2)
    email: str
    telefone: str = Field(min_length=8)


class CompletarPerfilRequest(BaseModel):
    cpf: str = Field(min_length=11)
    cnpj: str | None = None
    endereco: str = Field(min_length=8)


class ConfiguracaoSecretariaRequest(BaseModel):
    sobre_nutricionista: str = Field(min_length=10)
    tipos_atendimento: str = Field(min_length=5)
    especialidade: str = Field(min_length=3)
    publico_alvo: str = Field(min_length=3)
    periodo_trabalho: str = Field(min_length=3)
    disponibilidade_agenda: str = Field(min_length=3)
    preco_consulta: str = Field(min_length=1)
    pacotes_atendimento: str = Field(min_length=10)
    metodo_atendimento: str = Field(min_length=3)
    endereco_consulta_presencial: str | None = None
    instagram: str | None = None
    facebook: str | None = None
    telefone_profissional: str | None = None
    site: str | None = None
    contatos_adicionais: str | None = None
    google_agenda_configurada: bool = False
    asaas_configurada: bool = False
    primeira_inbox_configurada: bool = False


def _load_metadata(nutri: Nutricionista) -> dict:
    if not nutri.permissoes:
        return {}
    if isinstance(nutri.permissoes, dict):
        return nutri.permissoes
    try:
        return json.loads(nutri.permissoes)
    except Exception:
        return {}


def _save_metadata(nutri: Nutricionista, metadata: dict) -> None:
    nutri.permissoes = json.dumps(metadata, ensure_ascii=False)


def _resolver_limite_inboxes(db: Session, plano_nome: str) -> int:
    plano = (
        db.query(Plano)
        .filter(Plano.nome == plano_nome, Plano.ativo == 1)
        .order_by(Plano.id.desc())
        .first()
    )
    if plano:
        return int(plano.limite_caixas)
    limites_padrao = {"basic": 1, "pro": 5, "enterprise": 20}
    return limites_padrao.get(plano_nome.lower(), 1)


def _provisionar_nutri(
    db: Session,
    nome: str,
    email: str,
    plano_nome: str,
    auditoria_tag: str,
    telefone: str | None = None,
) -> tuple[Tenant, Nutricionista, ChatwootAccount, str]:
    limite_inboxes = _resolver_limite_inboxes(db, plano_nome)
    tenant = Tenant(
        nome=f"tenant-{nome.strip()}",
        plano=plano_nome,
        status="active",
        limites=json.dumps({"inboxes_base": limite_inboxes}),
        auditoria=auditoria_tag,
    )
    db.add(tenant)
    db.commit()
    db.refresh(tenant)

    senha_temporaria = gerar_senha_temporaria()
    metadata = {
        "temporary_password": True,
        "profile_completed": False,
        "setup_completed": False,
        "onboarding_source": "worker",
        "profile": {"telefone": telefone},
    }
    nutricionista = Nutricionista(
        nome=nome.strip(),
        email=email,
        password_hash=get_password_hash(senha_temporaria),
        status="active",
        plano=plano_nome,
        tenant_id=tenant.id,
        tipo_user="nutri",
        permissoes=json.dumps(metadata, ensure_ascii=False),
    )
    db.add(nutricionista)
    db.commit()
    db.refresh(nutricionista)

    provisionamento = provisionar_conta_chatwoot(nutricionista.nome, tenant.id)
    conta_chatwoot = ChatwootAccount(
        tenant_id=tenant.id,
        nutricionista_id=nutricionista.id,
        chatwoot_account_id=provisionamento["chatwoot_account_id"],
        chatwoot_account_external_id=provisionamento["chatwoot_account_id"],
        chatwoot_instance=provisionamento["chatwoot_instance"],
        limite_inboxes_base=limite_inboxes,
        inboxes_extra=0,
        status="active",
        criado_em=datetime.now(UTC),
        atualizado_em=datetime.now(UTC),
        observacoes="Conta criada automaticamente após confirmação de pagamento.",
    )
    db.add(conta_chatwoot)
    db.commit()
    db.refresh(conta_chatwoot)
    return tenant, nutricionista, conta_chatwoot, senha_temporaria


@router.post("/assinatura/confirmar", response_model=dict)
def confirmar_assinatura(
    data: ConfirmarAssinaturaRequest,
    db: Session = Depends(get_db),
):
    existente = db.query(Nutricionista).filter(Nutricionista.email == data.email).first()
    if existente:
        raise HTTPException(status_code=400, detail="E-mail já possui assinatura ativa")

    tenant, nutricionista, conta_chatwoot, senha_temporaria = _provisionar_nutri(
        db=db,
        nome=data.nome,
        email=data.email,
        plano_nome=data.plano_nome,
        auditoria_tag=f"assinatura_confirmada:{data.pagamento_id}",
        telefone=data.telefone,
    )

    email = enviar_email_boas_vindas_assinatura(
        email=nutricionista.email,
        nome=nutricionista.nome,
        senha_temporaria=senha_temporaria,
        plano=nutricionista.plano,
        limite_inboxes=conta_chatwoot.limite_inboxes_base + conta_chatwoot.inboxes_extra,
    )

    return {
        "status": "assinatura_confirmada",
        "tenant_id": tenant.id,
        "nutricionista_id": nutricionista.id,
        "chatwoot_account": conta_chatwoot.chatwoot_account_id,
        "chatwoot_instance": conta_chatwoot.chatwoot_instance,
        "limite_inboxes": conta_chatwoot.limite_inboxes_base + conta_chatwoot.inboxes_extra,
        "email_enviado": True,
        "email_assunto": email["assunto"],
        "proximo_passo": "Acessar o painel e solicitar integrações das inboxes desejadas.",
    }


@router.post("/trial/solicitar", response_model=dict)
def solicitar_trial(data: SolicitarTrialRequest, db: Session = Depends(get_db)):
    existente = db.query(Nutricionista).filter(Nutricionista.email == data.email).first()
    if existente:
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")

    tenant, nutricionista, conta_chatwoot, senha_temporaria = _provisionar_nutri(
        db=db,
        nome=data.nome,
        email=data.email,
        plano_nome="trial",
        auditoria_tag=f"trial_solicitado:{datetime.now(UTC).isoformat()}",
        telefone=data.telefone,
    )

    email = enviar_email_boas_vindas_assinatura(
        email=nutricionista.email,
        nome=nutricionista.nome,
        senha_temporaria=senha_temporaria,
        plano="trial",
        limite_inboxes=conta_chatwoot.limite_inboxes_base + conta_chatwoot.inboxes_extra,
    )

    return {
        "status": "trial_solicitado",
        "tenant_id": tenant.id,
        "nutricionista_id": nutricionista.id,
        "email_enviado": True,
        "email_assunto": email["assunto"],
        "message": "Cadastro inicial recebido. Enviamos uma senha temporária por e-mail.",
    }


@router.patch("/perfil/pessoal", response_model=dict)
def completar_perfil_pessoal(
    data: CompletarPerfilRequest,
    current_user: Nutricionista = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    metadata = _load_metadata(current_user)
    profile = metadata.get("profile", {})
    if not isinstance(profile, dict):
        profile = {}
    profile.update(
        {
            "cpf": data.cpf.strip(),
            "cnpj": (data.cnpj or "").strip() or None,
            "endereco": data.endereco.strip(),
        }
    )
    metadata["profile"] = profile
    metadata["profile_completed"] = True
    _save_metadata(current_user, metadata)

    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return {"status": "perfil_atualizado", "profile_completed": True}


@router.patch("/configuracao-inicial", response_model=dict)
def salvar_configuracao_inicial(
    data: ConfiguracaoSecretariaRequest,
    current_user: Nutricionista = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    metadata = _load_metadata(current_user)
    metadata["setup"] = data.dict()
    metadata["setup_completed"] = True
    _save_metadata(current_user, metadata)
    current_user.auditoria = json.dumps(
        {
            "sobre_nutricionista": data.sobre_nutricionista,
            "tipos_atendimento": data.tipos_atendimento,
            "especialidade": data.especialidade,
            "publico_alvo": data.publico_alvo,
        },
        ensure_ascii=False,
    )

    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return {"status": "configuracao_concluida", "setup_completed": True}
