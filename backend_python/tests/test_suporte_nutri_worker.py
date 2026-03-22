import os
import re
from datetime import UTC, datetime, timedelta

os.environ["TEST_ENV"] = "1"

from app.api.v1.auth import get_password_hash
from app.db import SessionLocal, init_db
from app.domain.models.agenda_evento import AgendaEvento
from app.domain.models.arquivo import Arquivo
from app.domain.models.cliente import Cliente
from app.domain.models.conversa import Conversa
from app.domain.models.google_calendar_integration import GoogleCalendarIntegration
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
    db.query(AgendaEvento).delete()
    db.query(Conversa).delete()
    db.query(GoogleCalendarIntegration).delete()
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


def test_suporte_nutri_escalacao_para_admin(monkeypatch):
    db, nutri, _ = _setup()
    sent = []
    admin_alerts = []
    monkeypatch.setattr(
        "app.workers.suporte_nutri_worker.enviar_mensagens",
        lambda _a, _c, msgs: sent.extend(msgs),
    )
    monkeypatch.setattr(
        "app.workers.suporte_nutri_worker.notificar_admins",
        lambda msg: admin_alerts.append(msg),
    )

    process_comando_chatwoot(
        "acct-1",
        "conv-1",
        "quero falar com o admin sobre um problema técnico",
        nutri.id,
        db,
    )
    assert any("solicitação ao admin" in m.lower() for m in sent)
    assert any("solicitacao-admin" in m for m in admin_alerts)
    db.close()


def test_comando_remarcacao_lote_amanha_proxima_semana_tarde(monkeypatch):
    db, nutri, cliente = _setup()
    sent = []
    monkeypatch.setattr(
        "app.workers.suporte_nutri_worker.enviar_mensagens",
        lambda _a, _c, msgs: sent.extend(msgs),
    )
    monkeypatch.setattr(
        "app.workers.suporte_nutri_worker.gerar_resposta_agente",
        lambda *args, **kwargs: '{"action":"bulk_reschedule_tomorrow_nextweek_afternoon","confidence":0.96}',
    )
    monkeypatch.setattr("app.workers.suporte_nutri_worker.publish_event", lambda *_a, **_k: True)

    now_utc = datetime.now(UTC).replace(tzinfo=None)
    tomorrow = (now_utc + timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0)
    evento = AgendaEvento(
        tenant_id=nutri.tenant_id,
        nutricionista_id=nutri.id,
        cliente_id=cliente.id,
        titulo="Consulta Joana",
        inicio_em=tomorrow,
        fim_em=tomorrow + timedelta(hours=1),
        status="agendado",
        origem="painel",
    )
    db.add(evento)
    db.commit()

    conv_cliente = Conversa(
        cliente_id=cliente.id,
        nutricionista_id=nutri.id,
        mensagem="canal ativo",
        data=now_utc,
        modo="ia",
        chatwoot_account_id="acct-1",
        chatwoot_conversation_id="conv-cliente-1",
    )
    db.add(conv_cliente)
    db.commit()

    process_comando_chatwoot(
        "acct-1",
        "conv-1",
        "contate todas as minhas clientes que possuem consulta amanha e remarque para proxima semana a tarde",
        nutri.id,
        db,
    )
    m = re.search(r"confirmo\s+([A-Z0-9]+)", " ".join(sent))
    assert m is not None
    token = m.group(1)
    sent.clear()
    process_comando_chatwoot("acct-1", "conv-1", f"confirmo {token}", nutri.id, db)

    db.refresh(evento)
    assert evento.inicio_em.weekday() <= 4
    assert evento.inicio_em.hour >= 13
    assert any("Remarcação em lote concluída" in msg for msg in sent)
    db.close()


def test_comando_remarcacao_customizada_por_data(monkeypatch):
    db, nutri, cliente = _setup()
    sent = []
    monkeypatch.setattr(
        "app.workers.suporte_nutri_worker.enviar_mensagens",
        lambda _a, _c, msgs: sent.extend(msgs),
    )
    monkeypatch.setattr(
        "app.workers.suporte_nutri_worker.gerar_resposta_agente",
        lambda *args, **kwargs: (
            '{"action":"reschedule_consultations","source_date":"2026-03-25","target_date":"2026-03-28",'
            '"target_period":"afternoon","scope":"all_on_source_date","confidence":0.95}'
        ),
    )
    monkeypatch.setattr("app.workers.suporte_nutri_worker.publish_event", lambda *_a, **_k: True)

    origem = datetime(2026, 3, 25, 10, 0, 0)
    evento = AgendaEvento(
        tenant_id=nutri.tenant_id,
        nutricionista_id=nutri.id,
        cliente_id=cliente.id,
        titulo="Consulta Joana",
        inicio_em=origem,
        fim_em=origem + timedelta(hours=1),
        status="agendado",
        origem="painel",
    )
    db.add(evento)
    db.commit()

    process_comando_chatwoot(
        "acct-1",
        "conv-1",
        "remarque as consultas de 2026-03-25 para 2026-03-28 a tarde",
        nutri.id,
        db,
    )
    m = re.search(r"confirmo\s+([A-Z0-9]+)", " ".join(sent))
    assert m is not None
    token = m.group(1)
    sent.clear()
    process_comando_chatwoot("acct-1", "conv-1", f"confirmo {token}", nutri.id, db)

    db.refresh(evento)
    assert evento.inicio_em.date().isoformat() == "2026-03-28"
    assert evento.inicio_em.hour >= 13
    assert any("Destino: 2026-03-28" in msg for msg in sent)
    db.close()


def test_comando_horarios_livres_por_data(monkeypatch):
    db, nutri, cliente = _setup()
    sent = []
    monkeypatch.setattr(
        "app.workers.suporte_nutri_worker.enviar_mensagens",
        lambda _a, _c, msgs: sent.extend(msgs),
    )

    # Ajusta setup com duração padrão da consulta
    nutri.permissoes = (
        '{"setup":{"periodo_trabalho":"08:00-18:00","disponibilidade_agenda":"08:00-18:00","duracao_consulta_minutos":60}}'
    )
    db.add(nutri)
    db.commit()

    data_ref = datetime(2026, 3, 27, 0, 0, 0)
    evento = AgendaEvento(
        tenant_id=nutri.tenant_id,
        nutricionista_id=nutri.id,
        cliente_id=cliente.id,
        titulo="Consulta ocupada",
        inicio_em=data_ref.replace(hour=9, minute=0),
        fim_em=data_ref.replace(hour=10, minute=0),
        status="agendado",
        origem="painel",
    )
    db.add(evento)
    db.commit()

    process_comando_chatwoot(
        "acct-1",
        "conv-1",
        "quais horarios livres eu tenho para o dia 2026-03-27",
        nutri.id,
        db,
    )
    assert any("Horários livres em 27/03/2026" in msg for msg in sent)
    assert any("09:00 às 10:00" not in msg for msg in sent)
    db.close()


def test_comando_ver_agenda_por_data_com_retorno_organizado(monkeypatch):
    db, nutri, cliente = _setup()
    sent = []
    monkeypatch.setattr(
        "app.workers.suporte_nutri_worker.enviar_mensagens",
        lambda _a, _c, msgs: sent.extend(msgs),
    )

    evento_data = datetime(2026, 4, 2, 14, 0, 0)
    evento = AgendaEvento(
        tenant_id=nutri.tenant_id,
        nutricionista_id=nutri.id,
        cliente_id=cliente.id,
        titulo="Consulta Joana",
        inicio_em=evento_data,
        fim_em=evento_data + timedelta(hours=1),
        status="agendado",
        origem="painel",
    )
    db.add(evento)
    db.commit()

    process_comando_chatwoot(
        "acct-1",
        "conv-1",
        "quero ver minha agenda de 2026-04-02",
        nutri.id,
        db,
    )
    resposta = "\n".join(sent)
    assert "Agenda 2026-04-02" in resposta
    assert "Cliente: Joana" in resposta
    assert "Data: 02/04/2026" in resposta
    assert "Hora: 14:00 às 15:00" in resposta
    db.close()


def test_contatar_cliente_nao_cadastrado_pede_dados_basicos(monkeypatch):
    db, nutri, _ = _setup()
    sent = []
    monkeypatch.setattr(
        "app.workers.suporte_nutri_worker.enviar_mensagens",
        lambda _a, _c, msgs: sent.extend(msgs),
    )

    process_comando_chatwoot(
        "acct-1",
        "conv-1",
        "faça um contato com fulano e acerte os detalhes sobre uma consulta comigo",
        nutri.id,
        db,
    )
    assert any("nome, contato" in msg.lower() for msg in sent)
    db.close()


def test_contatar_cliente_novo_com_dados_cadastra_e_liga(monkeypatch):
    db, nutri, _ = _setup()
    sent = []
    monkeypatch.setattr(
        "app.workers.suporte_nutri_worker.enviar_mensagens",
        lambda _a, _c, msgs: sent.extend(msgs),
    )

    process_comando_chatwoot(
        "acct-1",
        "conv-1",
        "cadastre novo cliente nome Maria Souza contato +55 11 98888-7777 status ativo e faça contato para acertar consulta",
        nutri.id,
        db,
    )
    m = re.search(r"confirmo\s+([A-Z0-9]+)", " ".join(sent))
    assert m is not None
    token = m.group(1)
    sent.clear()
    process_comando_chatwoot("acct-1", "conv-1", f"confirmo {token}", nutri.id, db)

    cliente = db.query(Cliente).filter(Cliente.contato_chatwoot == "+5511988887777").first()
    assert cliente is not None
    assert cliente.status == "cliente_ativo"

    call = db.query(VoiceCall).filter(VoiceCall.cliente_id == cliente.id).first()
    assert call is not None
    assert any("cadastrada e contato iniciado" in msg.lower() for msg in sent)
    db.close()
