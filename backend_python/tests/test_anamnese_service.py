import os
import uuid
from datetime import UTC, datetime, timedelta

os.environ["TEST_ENV"] = "1"

from app.db import SessionLocal, init_db
from app.domain.models.agenda_evento import AgendaEvento
from app.domain.models.anamnese_workflow import AnamneseWorkflow
from app.domain.models.cliente import Cliente
from app.domain.models.conversa import Conversa
from app.domain.models.nutricionista import Nutricionista
from app.domain.models.pagamento import Pagamento
from app.domain.models.tenant import Tenant
from app.services.anamnese_service import ensure_anamnese_workflow_for_cliente, process_anamnese_message


def _reset(db):
    db.query(AnamneseWorkflow).delete()
    db.query(AgendaEvento).delete()
    db.query(Pagamento).delete()
    db.query(Conversa).delete()
    db.query(Cliente).delete()
    db.query(Nutricionista).delete()
    db.query(Tenant).delete()
    db.commit()


def _seed_base(db):
    tenant = Tenant(nome="Tenant Anamnese", status="active", plano="pro")
    db.add(tenant)
    db.commit()
    db.refresh(tenant)

    nutri = Nutricionista(
        nome="Nutri Ana",
        email=f"ana-{uuid.uuid4()}@test.com",
        password_hash="hash",
        plano="pro",
        status="active",
        tenant_id=tenant.id,
        tipo_user="nutri",
    )
    db.add(nutri)
    db.commit()
    db.refresh(nutri)

    cliente = Cliente(
        nome="Paciente Joana",
        contato_chatwoot=f"cw-{uuid.uuid4()}",
        status="cliente_ativo",
        nutricionista_id=nutri.id,
    )
    db.add(cliente)
    db.commit()
    db.refresh(cliente)

    db.add(
        Conversa(
            cliente_id=cliente.id,
            nutricionista_id=nutri.id,
            caixa_id=None,
            chatwoot_account_id="acct-1",
            chatwoot_inbox_id="inbox-1",
            canal_origem="whatsapp",
            chatwoot_conversation_id="conv-1",
            mensagem="Olá",
            data=datetime.utcnow(),
            modo="ia",
            contexto_ia="",
            em_conversa_direta=False,
        )
    )
    db.commit()
    return tenant, nutri, cliente


def test_ensure_anamnese_workflow_for_cliente_cria_fluxo():
    init_db()
    db = SessionLocal()
    try:
        _reset(db)
        tenant, nutri, cliente = _seed_base(db)
        pagamento = Pagamento(
            cliente_id=cliente.id,
            nutricionista_id=nutri.id,
            valor=450.0,
            metodo="pix",
            status="pago",
            referencia="pay-ana-1",
        )
        db.add(pagamento)
        db.commit()
        db.refresh(pagamento)

        db.add(
            AgendaEvento(
                tenant_id=tenant.id,
                nutricionista_id=nutri.id,
                cliente_id=cliente.id,
                titulo="Consulta inicial",
                descricao="Primeira consulta",
                inicio_em=datetime.now(UTC).replace(tzinfo=None) + timedelta(days=5),
                fim_em=datetime.now(UTC).replace(tzinfo=None) + timedelta(days=5, minutes=50),
                status="agendado",
                origem="painel",
                criado_em=datetime.utcnow(),
                atualizado_em=datetime.utcnow(),
            )
        )
        db.commit()

        wf = ensure_anamnese_workflow_for_cliente(
            db,
            cliente_id=cliente.id,
            nutricionista_id=nutri.id,
            tenant_id=tenant.id,
            pagamento_id=pagamento.id,
            origin="test",
        )
        assert wf is not None
        assert wf.status == "pending"
        assert wf.pagamento_id == pagamento.id
        assert wf.prazo_conclusao_em is not None
    finally:
        db.close()


def test_process_anamnese_message_conclui_quando_campos_principais_informados():
    init_db()
    db = SessionLocal()
    try:
        _reset(db)
        tenant, nutri, cliente = _seed_base(db)
        db.add(
            AgendaEvento(
                tenant_id=tenant.id,
                nutricionista_id=nutri.id,
                cliente_id=cliente.id,
                titulo="Consulta inicial",
                descricao="Primeira consulta",
                inicio_em=datetime.now(UTC).replace(tzinfo=None) + timedelta(days=6),
                fim_em=datetime.now(UTC).replace(tzinfo=None) + timedelta(days=6, minutes=50),
                status="agendado",
                origem="painel",
                criado_em=datetime.utcnow(),
                atualizado_em=datetime.utcnow(),
            )
        )
        db.commit()

        wf = ensure_anamnese_workflow_for_cliente(
            db,
            cliente_id=cliente.id,
            nutricionista_id=nutri.id,
            tenant_id=tenant.id,
            origin="test",
        )
        assert wf is not None

        msg = (
            "Meu objetivo é emagrecer. Tenho histórico de hipertensão, uso medicamento diário, "
            "não tenho alergia. Meu café, almoço e jantar são em casa. Bebo 2 litros de agua, "
            "durmo 7 horas, faço atividade física na academia 4x semana. Peso 72kg e altura 1,67m. "
            "Vou enviar foto do prato."
        )
        handled, reply = process_anamnese_message(db, cliente=cliente, nutri=nutri, message=msg)
        assert handled is True
        assert reply is not None

        db.refresh(wf)
        assert wf.status == "completed"
        assert wf.concluido_em is not None
    finally:
        db.close()
