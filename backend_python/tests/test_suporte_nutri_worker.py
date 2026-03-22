import os
import re

os.environ["TEST_ENV"] = "1"

from app.api.v1.auth import get_password_hash
from app.db import SessionLocal, init_db
from app.domain.models.arquivo import Arquivo
from app.domain.models.cliente import Cliente
from app.domain.models.nutri_action_confirmation import NutriActionConfirmation
from app.domain.models.nutricionista import Nutricionista
from app.domain.models.plano_alimentar import PlanoAlimentar
from app.domain.models.tenant import Tenant
from app.domain.models.voice_call import VoiceCall
from app.domain.models.worker_job import WorkerJob
from app.workers.suporte_nutri_worker import process_comando_chatwoot


def _setup():
    init_db()
    db = SessionLocal()
    db.query(Arquivo).delete()
    db.query(PlanoAlimentar).delete()
    db.query(NutriActionConfirmation).delete()
    db.query(WorkerJob).delete()
    db.query(VoiceCall).delete()
    db.query(Cliente).delete()
    db.query(Nutricionista).delete()
    db.query(Tenant).delete()
    db.commit()

    tenant = Tenant(nome="Tenant Comando", status="active", plano="pro")
    db.add(tenant)
    db.commit()
    db.refresh(tenant)

    nutri = Nutricionista(
        nome="Nutri Comando",
        email="nutri.comando@test.com",
        password_hash=get_password_hash("senha123"),
        status="active",
        plano="pro",
        tenant_id=tenant.id,
        tipo_user="nutri",
    )
    db.add(nutri)
    db.commit()
    db.refresh(nutri)

    cliente = Cliente(
        nome="Joana",
        contato_chatwoot="+5511999999999",
        status="cliente_ativo",
        nutricionista_id=nutri.id,
    )
    db.add(cliente)
    db.commit()
    db.refresh(cliente)

    plano = PlanoAlimentar(
        cliente_id=cliente.id,
        nutricionista_id=nutri.id,
        titulo="Plano base Joana",
        descricao="Plano alimentar com foco em rotina semanal.",
        macros='{"proteina":"120g"}',
        refeicoes='["cafe","almoco","jantar"]',
        status="ativo",
    )
    db.add(plano)
    db.commit()

    return db, nutri, cliente


def test_comando_ligacao_natural_language_cria_chamada_e_job(monkeypatch):
    db, nutri, cliente = _setup()
    sent = []
    monkeypatch.setattr(
        "app.workers.suporte_nutri_worker.enviar_mensagens",
        lambda _a, _c, msgs: sent.extend(msgs),
    )
    monkeypatch.setattr(
        "app.workers.suporte_nutri_worker.gerar_resposta_agente",
        lambda *args, **kwargs: '{"action":"call_client","client_name":"Joana","objective":"Ligar e reagendar","confidence":0.9}',
    )
    process_comando_chatwoot(
        "acct-1",
        "conv-1",
        "Ligue para Joana e reagende a consulta para outro dia disponível nesta semana.",
        nutri.id,
        db,
    )
    m = re.search(r"confirmo\s+([A-Z0-9]+)", " ".join(sent))
    assert m is not None
    token = m.group(1)
    process_comando_chatwoot("acct-1", "conv-1", f"confirmo {token}", nutri.id, db)

    call = db.query(VoiceCall).filter(VoiceCall.nutricionista_id == nutri.id, VoiceCall.cliente_id == cliente.id).first()
    assert call is not None
    assert call.status == "queued"

    job = db.query(WorkerJob).filter(WorkerJob.tipo == "voice_call_create", WorkerJob.cliente_id == cliente.id).first()
    assert job is not None
    assert job.queue == "queue.voice.call"
    db.close()


def test_comando_mensagem_voz_natural_language_cria_job(monkeypatch):
    db, nutri, cliente = _setup()
    sent = []
    monkeypatch.setattr(
        "app.workers.suporte_nutri_worker.enviar_mensagens",
        lambda _a, _c, msgs: sent.extend(msgs),
    )
    monkeypatch.setattr(
        "app.workers.suporte_nutri_worker.gerar_resposta_agente",
        lambda *args, **kwargs: '{"action":"send_voice_message","client_name":"Joana","message":"Consulta confirmada para quinta","confidence":0.92}',
    )
    process_comando_chatwoot(
        "acct-1",
        "conv-1",
        "Envie mensagem de voz para Joana: consulta confirmada para quinta-feira às 15h.",
        nutri.id,
        db,
    )
    m = re.search(r"confirmo\s+([A-Z0-9]+)", " ".join(sent))
    assert m is not None
    token = m.group(1)
    process_comando_chatwoot("acct-1", "conv-1", f"confirmo {token}", nutri.id, db)

    job = db.query(WorkerJob).filter(WorkerJob.tipo == "voice_message_chatwoot", WorkerJob.cliente_id == cliente.id).first()
    assert job is not None
    assert job.queue == "queue.voice.call"
    db.close()


def test_comando_copia_plano_alimentar_interpretado_por_ia(monkeypatch):
    db, nutri, _ = _setup()
    sent_messages = []
    monkeypatch.setattr(
        "app.workers.suporte_nutri_worker.gerar_resposta_agente",
        lambda *args, **kwargs: '{"action":"send_meal_plan_copy","client_name":"Joana","confidence":0.95}'
        if "Schema" in (args[1] if len(args) > 1 else "")
        else "Resumo do plano alimentar da Joana.",
    )
    monkeypatch.setattr(
        "app.workers.suporte_nutri_worker.enviar_mensagens",
        lambda _a, _c, msgs: sent_messages.extend(msgs),
    )
    monkeypatch.setattr("app.workers.suporte_nutri_worker.download_object", lambda *_args, **_kwargs: False)

    process_comando_chatwoot(
        "acct-1",
        "conv-1",
        "envie para mim uma cópia do plano alimentar da Joana",
        nutri.id,
        db,
    )
    m = re.search(r"confirmo\s+([A-Z0-9]+)", " ".join(sent_messages))
    assert m is not None
    token = m.group(1)
    process_comando_chatwoot("acct-1", "conv-1", f"confirmo {token}", nutri.id, db)

    assert any("cópia textual" in m.lower() or "resumo do plano" in m.lower() for m in sent_messages)
    db.close()


def test_comando_desconhecido_delega_para_especialista(monkeypatch):
    db, nutri, _ = _setup()
    sent = []
    monkeypatch.setattr(
        "app.workers.suporte_nutri_worker.enviar_mensagens",
        lambda _a, _c, msgs: sent.extend(msgs),
    )
    monkeypatch.setattr(
        "app.workers.suporte_nutri_worker.gerar_resposta_agente",
        lambda *args, **kwargs: '{"action":"delegate_specialist","specialist":"plano","objective":"Ajustar plano de cliente diabético","confidence":0.7}',
    )

    process_comando_chatwoot(
        "acct-1",
        "conv-1",
        "faça algo complexo sobre ajustes avançados",
        nutri.id,
        db,
    )
    m = re.search(r"confirmo\s+([A-Z0-9]+)", " ".join(sent))
    assert m is not None
    token = m.group(1)
    process_comando_chatwoot("acct-1", "conv-1", f"confirmo {token}", nutri.id, db)

    job = db.query(WorkerJob).filter(WorkerJob.tipo == "specialist_task", WorkerJob.queue == "queue.specialist").first()
    assert job is not None
    db.close()


def test_low_confidence_acao_sensivel_nao_executa(monkeypatch):
    db, nutri, _ = _setup()
    sent = []
    monkeypatch.setattr(
        "app.workers.suporte_nutri_worker.enviar_mensagens",
        lambda _a, _c, msgs: sent.extend(msgs),
    )
    monkeypatch.setattr(
        "app.workers.suporte_nutri_worker.gerar_resposta_agente",
        lambda *args, **kwargs: '{"action":"call_client","client_name":"Joana","objective":"Ligar","confidence":0.3}',
    )
    process_comando_chatwoot("acct-1", "conv-1", "ligue para Joana", nutri.id, db)
    assert any("confirmação adicional" in m.lower() for m in sent)
    assert db.query(VoiceCall).count() == 0
    db.close()
