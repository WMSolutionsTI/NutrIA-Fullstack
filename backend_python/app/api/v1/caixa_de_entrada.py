from datetime import UTC, datetime
import json
import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.v1.auth import get_current_user
from app.db import get_db
from app.domain.models.admin_request import AdminRequest
from app.domain.models.caixa_de_entrada import CaixaDeEntrada
from app.domain.models.chatwoot_account import ChatwootAccount
from app.domain.models.nutricionista import Nutricionista
from app.workers.admin_monitor_worker import notificar_admins

router = APIRouter(prefix="/caixas", tags=["Caixas de Entrada"])


class CaixaCreateRequest(BaseModel):
    tipo: str = Field(min_length=2)
    identificador_chatwoot: str | None = None
    nutricionista_id: int | None = None
    detalhes_integracao: dict | None = None


class InboxExtraRequest(BaseModel):
    quantidade: int = Field(default=1, ge=1, le=100)


def _get_nutri_alvo(
    db: Session, current_user: Nutricionista, nutricionista_id: int | None
) -> Nutricionista:
    alvo_id = nutricionista_id or current_user.id
    nutri = db.query(Nutricionista).filter(Nutricionista.id == alvo_id).first()
    if not nutri:
        raise HTTPException(status_code=404, detail="Nutricionista não encontrado")

    if current_user.papel != "admin" and nutri.id != current_user.id:
        raise HTTPException(status_code=403, detail="Acesso negado")

    if (
        current_user.papel != "admin"
        and current_user.tenant_id
        and nutri.tenant_id != current_user.tenant_id
    ):
        raise HTTPException(status_code=403, detail="Tenant inválido")
    return nutri


def _get_conta_chatwoot_or_404(db: Session, nutri_id: int) -> ChatwootAccount:
    conta = (
        db.query(ChatwootAccount)
        .filter(ChatwootAccount.nutricionista_id == nutri_id, ChatwootAccount.status == "active")
        .first()
    )
    if not conta:
        raise HTTPException(status_code=400, detail="Conta Chatwoot ainda não provisionada para essa nutricionista")
    return conta


def _limite_total_inboxes(conta: ChatwootAccount) -> int:
    return int(conta.limite_inboxes_base or 0) + int(conta.inboxes_extra or 0)


@router.get("/resumo", response_model=dict)
def resumo_caixas(
    db: Session = Depends(get_db),
    current_user: Nutricionista = Depends(get_current_user),
):
    nutri = current_user
    conta = _get_conta_chatwoot_or_404(db, nutri.id)
    em_uso = (
        db.query(CaixaDeEntrada)
        .filter(
            CaixaDeEntrada.nutricionista_id == nutri.id,
            CaixaDeEntrada.status != "deleted",
        )
        .count()
    )
    limite_total = _limite_total_inboxes(conta)
    return {
        "nutricionista_id": nutri.id,
        "tenant_id": nutri.tenant_id,
        "plano": nutri.plano,
        "chatwoot_account_id": conta.chatwoot_account_id,
        "chatwoot_account_external_id": conta.chatwoot_account_external_id,
        "chatwoot_instance": conta.chatwoot_instance,
        "limite_inboxes_base": int(conta.limite_inboxes_base or 0),
        "inboxes_extra": int(conta.inboxes_extra or 0),
        "limite_total": limite_total,
        "em_uso": em_uso,
        "disponiveis": max(limite_total - em_uso, 0),
    }


@router.get("/pendencias", response_model=list)
def pendencias_caixas(
    db: Session = Depends(get_db),
    current_user: Nutricionista = Depends(get_current_user),
):
    query = db.query(AdminRequest).filter(AdminRequest.tipo == "nova_integracao_inbox")
    if current_user.papel == "admin":
        pendencias = query.order_by(AdminRequest.criado_em.desc()).all()
    else:
        pendencias = query.filter(
            AdminRequest.nutricionista_id == current_user.id
        ).order_by(AdminRequest.criado_em.desc()).all()

    parsed = []
    for item in pendencias:
        detalhes = None
        if item.descricao:
            try:
                detalhes = json.loads(item.descricao)
            except Exception:
                detalhes = {"descricao_raw": item.descricao}
        parsed.append(
            {
                "id": item.id,
                "status": item.status,
                "tipo": item.tipo,
                "nutricionista_id": item.nutricionista_id,
                "tenant_id": item.tenant_id,
                "detalhes": detalhes,
                "criado_em": item.criado_em.isoformat() if item.criado_em else None,
                "atualizado_em": item.atualizado_em.isoformat() if item.atualizado_em else None,
            }
        )
    return parsed


@router.get("/", response_model=list)
def list_caixas(
    db: Session = Depends(get_db),
    current_user: Nutricionista = Depends(get_current_user),
):
    query = db.query(CaixaDeEntrada)
    if current_user.papel != "admin":
        query = query.filter(CaixaDeEntrada.nutricionista_id == current_user.id)
    return query.all()


@router.post("/", response_model=dict)
def create_caixa(
    caixa: CaixaCreateRequest,
    db: Session = Depends(get_db),
    current_user: Nutricionista = Depends(get_current_user),
):
    nutri = _get_nutri_alvo(db, current_user, caixa.nutricionista_id)
    conta = _get_conta_chatwoot_or_404(db, nutri.id)

    caixas_ativas = (
        db.query(CaixaDeEntrada)
        .filter(CaixaDeEntrada.nutricionista_id == nutri.id, CaixaDeEntrada.status != "deleted")
        .count()
    )
    limite_total = _limite_total_inboxes(conta)
    if caixas_ativas >= limite_total:
        raise HTTPException(
            status_code=403,
            detail="Limite de inboxes atingido. Adquira inbox avulsa ou faça upgrade do plano.",
        )

    identificador = caixa.identificador_chatwoot or f"pending-{uuid.uuid4().hex[:12]}"
    status = "pending_setup" if caixa.identificador_chatwoot is None else "active"
    nova_caixa = CaixaDeEntrada(
        tipo=caixa.tipo.lower(),
        identificador_chatwoot=identificador,
        nutricionista_id=nutri.id,
        status=status,
        data_aquisicao=datetime.now(UTC).isoformat(),
    )
    db.add(nova_caixa)
    db.commit()
    db.refresh(nova_caixa)

    if caixa.detalhes_integracao or status == "pending_setup":
        descricao = {
            "caixa_id": nova_caixa.id,
            "tipo": nova_caixa.tipo,
            "identificador": nova_caixa.identificador_chatwoot,
            "detalhes_integracao": caixa.detalhes_integracao or {},
        }
        pedido = AdminRequest(
            tenant_id=nutri.tenant_id,
            nutricionista_id=nutri.id,
            tipo="nova_integracao_inbox",
            status="pendente",
            descricao=json.dumps(descricao, ensure_ascii=False),
            criado_em=datetime.now(UTC),
            atualizado_em=datetime.now(UTC),
        )
        db.add(pedido)
        db.commit()
        db.refresh(pedido)
        notificar_admins(
            f"Nova integração pendente: nutri {nutri.id} solicitou inbox {nova_caixa.tipo} (caixa {nova_caixa.id})."
        )

    return {
        "id": nova_caixa.id,
        "status": nova_caixa.status,
        "nutricionista_id": nutri.id,
        "limite_total": limite_total,
        "em_uso": caixas_ativas + 1,
    }


@router.get("/{caixa_id}", response_model=dict)
def get_caixa(
    caixa_id: int,
    db: Session = Depends(get_db),
    current_user: Nutricionista = Depends(get_current_user),
):
    caixa = db.query(CaixaDeEntrada).filter(CaixaDeEntrada.id == caixa_id).first()
    if not caixa:
        raise HTTPException(status_code=404, detail="Caixa não encontrada")

    if current_user.papel != "admin" and caixa.nutricionista_id != current_user.id:
        raise HTTPException(status_code=403, detail="Acesso negado")
    return caixa.__dict__


@router.put("/{caixa_id}", response_model=dict)
def update_caixa(
    caixa_id: int,
    caixa_data: dict,
    db: Session = Depends(get_db),
    current_user: Nutricionista = Depends(get_current_user),
):
    caixa = db.query(CaixaDeEntrada).filter(CaixaDeEntrada.id == caixa_id).first()
    if not caixa:
        raise HTTPException(status_code=404, detail="Caixa não encontrada")
    if current_user.papel != "admin" and caixa.nutricionista_id != current_user.id:
        raise HTTPException(status_code=403, detail="Acesso negado")

    for k, v in caixa_data.items():
        if k in {"id", "nutricionista_id"}:
            continue
        setattr(caixa, k, v)
    db.commit()
    db.refresh(caixa)
    return caixa.__dict__


@router.delete("/{caixa_id}", response_model=dict)
def delete_caixa(
    caixa_id: int,
    db: Session = Depends(get_db),
    current_user: Nutricionista = Depends(get_current_user),
):
    caixa = db.query(CaixaDeEntrada).filter(CaixaDeEntrada.id == caixa_id).first()
    if not caixa:
        raise HTTPException(status_code=404, detail="Caixa não encontrada")
    if current_user.papel != "admin" and caixa.nutricionista_id != current_user.id:
        raise HTTPException(status_code=403, detail="Acesso negado")

    caixa.status = "deleted"
    db.commit()
    return {"status": "deleted", "id": caixa.id}


@router.post("/acquire", response_model=dict)
def acquire_caixa(
    payload: CaixaCreateRequest,
    db: Session = Depends(get_db),
    current_user: Nutricionista = Depends(get_current_user),
):
    return create_caixa(payload, db, current_user)


@router.post("/extras/comprar", response_model=dict)
def comprar_inbox_avulsa(
    payload: InboxExtraRequest,
    db: Session = Depends(get_db),
    current_user: Nutricionista = Depends(get_current_user),
):
    conta = _get_conta_chatwoot_or_404(db, current_user.id)
    conta.inboxes_extra = int(conta.inboxes_extra or 0) + payload.quantidade
    conta.atualizado_em = datetime.now(UTC)
    db.add(conta)
    db.commit()
    db.refresh(conta)
    return {
        "status": "inbox_extra_adquirida",
        "quantidade_adquirida": payload.quantidade,
        "novo_limite_total": _limite_total_inboxes(conta),
    }


@router.post("/upgrade", response_model=dict)
def upgrade_caixa(
    caixa_id: int,
    db: Session = Depends(get_db),
    current_user: Nutricionista = Depends(get_current_user),
):
    caixa = db.query(CaixaDeEntrada).filter(CaixaDeEntrada.id == caixa_id).first()
    if not caixa:
        raise HTTPException(status_code=404, detail="Caixa não encontrada")
    if current_user.papel != "admin" and caixa.nutricionista_id != current_user.id:
        raise HTTPException(status_code=403, detail="Acesso negado")

    caixa.status = "upgraded"
    db.commit()
    db.refresh(caixa)
    return {"id": caixa.id, "status": "upgraded"}
