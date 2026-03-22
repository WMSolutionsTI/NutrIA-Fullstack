from datetime import UTC, datetime, timedelta
import json
import os
import re
import secrets
import shutil
import socket
import smtplib
import subprocess
from email.mime.text import MIMEText

from passlib.context import CryptContext
from sqlalchemy import func, text

from app.db import SessionLocal
from app.domain.models.chatwoot_account import ChatwootAccount
from app.domain.models.cliente import Cliente
from app.domain.models.conversa import Conversa
from app.domain.models.nutricionista import Nutricionista
from app.domain.models.plano import Plano
from app.domain.models.tenant import Tenant
from app.domain.models.worker_job import WorkerJob
from app.services.ai_service import gerar_resposta_agente
from app.services.asaas_service import AsaasError, get_balance, is_configured, load_asaas_config_from_user
from app.services.worker_job_service import update_worker_job_status
from app.utils.text_normalize import normalize_pt_text
from app.workers.admin_monitor_worker import notificar_admins, status_do_sistema
from app.workers.cadastro_assinatura_worker import (
    enviar_email_boas_vindas_assinatura,
    gerar_senha_temporaria,
    provisionar_conta_chatwoot,
)
from app.workers.quebrar_enviar_mensagens_worker import enviar_mensagens
from app.workers.redis_worker import delete_cache, get_cache, redis_client, set_cache, set_if_not_exists

SUPPORTED_ACTIONS = {
    "system_state",
    "cluster_diagnosis",
    "queue_report",
    "scale_worker",
    "backup_database",
    "daily_followup_now",
    "daily_followup_enable",
    "daily_followup_disable",
    "send_email_nutri",
    "send_message_nutri",
    "broadcast_nutri_alert",
    "register_nutri",
    "asaas_account_info",
    "help",
    "unknown",
}

SENSITIVE_ACTIONS = {"scale_worker", "backup_database", "broadcast_nutri_alert", "register_nutri"}
CONFIRMATION_TTL_MINUTES = 10
PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _extract_json(texto: str) -> dict:
    if not texto:
        return {}
    texto = texto.strip()
    try:
        parsed = json.loads(texto)
        return parsed if isinstance(parsed, dict) else {}
    except Exception:
        pass
    match = re.search(r"\{.*\}", texto, flags=re.DOTALL)
    if not match:
        return {}
    try:
        parsed = json.loads(match.group(0))
        return parsed if isinstance(parsed, dict) else {}
    except Exception:
        return {}


def _decode_cache(raw) -> str:
    if raw is None:
        return ""
    if isinstance(raw, bytes):
        return raw.decode("utf-8", errors="ignore")
    return str(raw)


def _health_check_tcp(host: str, port: int, timeout_sec: float = 0.6) -> str:
    try:
        with socket.create_connection((host, port), timeout=timeout_sec):
            return "ok"
    except Exception:
        return "down"


def _hash_password(password: str) -> str:
    return PWD_CONTEXT.hash(password)


def _resolver_limite_inboxes(db: SessionLocal, plano_nome: str) -> int:
    plano = (
        db.query(Plano)
        .filter(Plano.nome == plano_nome, Plano.ativo == 1)
        .order_by(Plano.id.desc())
        .first()
    )
    if plano:
        return int(plano.limite_caixas)
    return {"trial": 1, "basic": 1, "pro": 5, "enterprise": 20}.get(plano_nome.lower(), 1)


def _provisionar_nutri_admin(
    db: SessionLocal,
    *,
    nome: str,
    email: str,
    plano_nome: str,
) -> tuple[Tenant, Nutricionista, ChatwootAccount, str]:
    limite_inboxes = _resolver_limite_inboxes(db, plano_nome)
    tenant = Tenant(
        nome=f"tenant-{nome.strip()}",
        plano=plano_nome,
        status="active",
        limites=json.dumps({"inboxes_base": limite_inboxes}),
        auditoria=f"admin_register:{datetime.now(UTC).isoformat()}",
    )
    db.add(tenant)
    db.commit()
    db.refresh(tenant)

    senha_temporaria = gerar_senha_temporaria()
    nutricionista = Nutricionista(
        nome=nome.strip(),
        email=email.strip().lower(),
        password_hash=_hash_password(senha_temporaria),
        status="active",
        plano=plano_nome,
        tenant_id=tenant.id,
        tipo_user="nutri",
        permissoes=json.dumps(
            {
                "temporary_password": True,
                "profile_completed": False,
                "setup_completed": False,
                "onboarding_source": "admin_ops",
            },
            ensure_ascii=False,
        ),
    )
    db.add(nutricionista)
    db.commit()
    db.refresh(nutricionista)

    provisionamento = provisionar_conta_chatwoot(nutricionista.nome, tenant.id)
    conta = ChatwootAccount(
        tenant_id=tenant.id,
        nutricionista_id=nutricionista.id,
        chatwoot_account_id=provisionamento["chatwoot_account_id"],
        chatwoot_account_external_id=provisionamento["chatwoot_account_id"],
        chatwoot_instance=provisionamento["chatwoot_instance"],
        limite_inboxes_base=limite_inboxes,
        inboxes_extra=0,
        status="active",
        criado_em=datetime.now(UTC).replace(tzinfo=None),
        atualizado_em=datetime.now(UTC).replace(tzinfo=None),
        observacoes="Conta criada via admin ops.",
    )
    db.add(conta)
    db.commit()
    db.refresh(conta)
    return tenant, nutricionista, conta, senha_temporaria


def _cluster_diag_summary(db: SessionLocal) -> str:
    jobs_grouped = db.query(WorkerJob.status, func.count(WorkerJob.id)).group_by(WorkerJob.status).all()
    jobs_status = {status: int(count) for status, count in jobs_grouped}
    failed_recent = (
        db.query(WorkerJob)
        .filter(WorkerJob.status == "failed")
        .order_by(WorkerJob.atualizado_em.desc())
        .limit(5)
        .all()
    )

    disk = shutil.disk_usage("/")
    disk_used_pct = (disk.used / disk.total) * 100 if disk.total else 0.0
    rabbit_status = _health_check_tcp(os.getenv("RABBITMQ_HOST", "rabbitmq"), int(os.getenv("RABBITMQ_PORT", "5672")))
    redis_status = "ok"
    try:
        redis_client.ping()
    except Exception:
        redis_status = "down"
    db_status = "ok"
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_status = "down"

    lines = [
        "Diagnóstico do cluster:",
        f"- timestamp_utc: {datetime.now(UTC).isoformat()}",
        f"- db: {db_status}",
        f"- rabbitmq({os.getenv('RABBITMQ_HOST', 'rabbitmq')}): {rabbit_status}",
        f"- redis({os.getenv('REDIS_HOST', 'redis')}): {redis_status}",
        f"- disk_used_pct: {disk_used_pct:.1f}%",
        f"- jobs: {jobs_status}",
    ]
    if failed_recent:
        lines.append("- últimas_falhas:")
        for job in failed_recent:
            lines.append(
                f"  • {job.tipo} ({job.queue}) event_id={job.event_id} tentativas={job.tentativas} erro={job.erro or '-'}"
            )
    return "\n".join(lines)


def _parse_confirm_command(message: str) -> tuple[str | None, str | None]:
    text = normalize_pt_text(message)
    m_confirm = re.search(r"\bconfirmo\s+([a-z0-9]{6,12})\b", text)
    if m_confirm:
        return "confirm", m_confirm.group(1).upper()
    m_cancel = re.search(r"\bcancelar\s+([a-z0-9]{6,12})\b", text)
    if m_cancel:
        return "cancel", m_cancel.group(1).upper()
    return None, None


def _extract_email_from_text(text: str) -> str:
    match = re.search(r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)", text or "")
    return (match.group(1).strip() if match else "")


def _extract_after_colon(text: str) -> str:
    if ":" in (text or ""):
        return text.split(":", 1)[1].strip()
    return ""


def _parse_admin_action(message: str) -> dict:
    lower = normalize_pt_text(message)
    if not lower:
        return {"action": "help", "confidence": 1.0}

    msg_content = _extract_after_colon(message)
    email_match = _extract_email_from_text(message)

    if ("estado" in lower or "status" in lower) and ("servidor" in lower or "sistema" in lower):
        return {"action": "system_state", "confidence": 0.95}
    if "diagn" in lower and ("cluster" in lower or "infra" in lower):
        return {"action": "cluster_diagnosis", "confidence": 0.95}
    if "fila" in lower:
        return {"action": "queue_report", "confidence": 0.95}
    if "backup" in lower and ("banco" in lower or "db" in lower):
        return {"action": "backup_database", "confidence": 0.95}
    if ("subir" in lower or "escalar" in lower or "aumentar" in lower) and "worker" in lower:
        replicas = 2 if "mais um" in lower else 0
        return {"action": "scale_worker", "confidence": 0.9, "worker_service": "worker_atendimento", "replicas": replicas}
    if ("followup" in lower or "follow-up" in lower or "relatório diário" in lower or "relatorio diario" in lower) and (
        "ativ" in lower or "lig" in lower
    ):
        return {"action": "daily_followup_enable", "confidence": 0.9}
    if ("followup" in lower or "follow-up" in lower or "relatório diário" in lower or "relatorio diario" in lower) and (
        "desativ" in lower or "deslig" in lower
    ):
        return {"action": "daily_followup_disable", "confidence": 0.9}
    if "asaas" in lower and ("conta" in lower or "saldo" in lower or "informa" in lower):
        return {"action": "asaas_account_info", "confidence": 0.95}
    if "alerta" in lower and "todos" in lower and "nutri" in lower:
        return {"action": "broadcast_nutri_alert", "confidence": 0.92, "message_content": msg_content}
    if ("enviar email" in lower or "mande email" in lower) and ("nutri" in lower or email_match):
        return {
            "action": "send_email_nutri",
            "confidence": 0.9,
            "target_query": email_match,
            "message_content": msg_content,
            "subject": "Comunicado da administração NutrIA-Pro",
        }
    if ("enviar mensagem" in lower or "avisar" in lower or "notificar" in lower) and "nutri" in lower:
        return {"action": "send_message_nutri", "confidence": 0.88, "target_query": email_match, "message_content": msg_content}
    if "cadastrar" in lower and "nutri" in lower:
        plan_match = re.search(r"\b(trial|basic|pro|enterprise)\b", lower)
        return {
            "action": "register_nutri",
            "confidence": 0.82,
            "novo_nome": "",
            "novo_email": email_match,
            "novo_plano": plan_match.group(1) if plan_match else "pro",
        }

    prompt = f"""
Você interpreta mensagens do admin do SaaS para operações técnicas e administrativas.
Responda SOMENTE JSON válido com schema:
{{
  "action":"system_state|cluster_diagnosis|queue_report|scale_worker|backup_database|daily_followup_now|daily_followup_enable|daily_followup_disable|send_email_nutri|send_message_nutri|broadcast_nutri_alert|register_nutri|asaas_account_info|help|unknown",
  "worker_service":"string ou vazio",
  "replicas":0,
  "target_query":"email/nome da nutri alvo ou vazio",
  "message_content":"texto da comunicação ou vazio",
  "subject":"assunto de email ou vazio",
  "novo_nome":"nome da nova nutri ou vazio",
  "novo_email":"email da nova nutri ou vazio",
  "novo_plano":"trial|basic|pro|enterprise|vazio",
  "confidence":0.0,
  "reason":"string"
}}
Mensagem: {message}
"""
    raw = gerar_resposta_agente("especialista_tech", prompt, model="gpt-4o-mini", temperature=0.1)
    parsed = _extract_json(raw)
    action = str(parsed.get("action") or "unknown").strip()
    if action not in SUPPORTED_ACTIONS:
        action = "unknown"
    return {
        "action": action,
        "worker_service": str(parsed.get("worker_service") or "").strip(),
        "replicas": int(parsed.get("replicas") or 0),
        "target_query": str(parsed.get("target_query") or "").strip(),
        "message_content": str(parsed.get("message_content") or "").strip(),
        "subject": str(parsed.get("subject") or "").strip(),
        "novo_nome": str(parsed.get("novo_nome") or "").strip(),
        "novo_email": str(parsed.get("novo_email") or "").strip(),
        "novo_plano": str(parsed.get("novo_plano") or "").strip(),
        "confidence": float(parsed.get("confidence") or 0),
        "reason": str(parsed.get("reason") or "").strip(),
    }


def _pending_key(account_id: str, conversation_id: str) -> str:
    return f"adminops:pending:{account_id}:{conversation_id}"


def _execute_scale_worker(worker_service: str, replicas: int) -> str:
    service = re.sub(r"[^a-zA-Z0-9_.-]", "", worker_service or "")
    if not service:
        return "Serviço de worker não informado."
    if replicas <= 0:
        return "Número de réplicas inválido."

    cmd_template = (os.getenv("ADMIN_OPS_SCALE_CMD") or "").strip()
    allow_mutation = os.getenv("ADMIN_OPS_ALLOW_CLUSTER_MUTATIONS", "0") == "1"
    if not allow_mutation:
        return f"[DRY-RUN] Escalonamento solicitado: {service} => {replicas} réplicas."
    if not cmd_template:
        return "ADMIN_OPS_SCALE_CMD não configurado."

    cmd = cmd_template.format(worker_service=service, replicas=replicas)
    completed = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=45)
    if completed.returncode != 0:
        return f"Falha ao escalar worker. stderr: {completed.stderr.strip()[:300]}"
    return f"Escalonamento executado com sucesso. output: {completed.stdout.strip()[:300] or 'ok'}"


def _execute_backup_database() -> str:
    cmd_template = (os.getenv("ADMIN_OPS_BACKUP_CMD") or "").strip()
    allow_mutation = os.getenv("ADMIN_OPS_ALLOW_CLUSTER_MUTATIONS", "0") == "1"
    if not allow_mutation:
        return "[DRY-RUN] Backup solicitado do banco de dados."
    if not cmd_template:
        return "ADMIN_OPS_BACKUP_CMD não configurado."
    completed = subprocess.run(cmd_template, shell=True, capture_output=True, text=True, timeout=120)
    if completed.returncode != 0:
        return f"Falha no backup. stderr: {completed.stderr.strip()[:300]}"
    return f"Backup executado com sucesso. output: {completed.stdout.strip()[:300] or 'ok'}"


def _find_nutri_by_query(db: SessionLocal, query: str) -> Nutricionista | None:
    q = (query or "").strip().lower()
    if not q:
        return None
    found = db.query(Nutricionista).filter(func.lower(Nutricionista.email) == q).first()
    if found:
        return found
    return (
        db.query(Nutricionista)
        .filter(Nutricionista.tipo_user == "nutri", func.lower(Nutricionista.nome).like(f"%{q}%"))
        .order_by(Nutricionista.id.desc())
        .first()
    )


def _smtp_send(email: str, subject: str, body: str) -> bool:
    if os.getenv("TEST_ENV", "0") == "1":
        return True
    host = os.getenv("SMTP_HOST")
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASSWORD")
    if not (host and user and password):
        return False
    port = int(os.getenv("SMTP_PORT", "587"))
    from_email = os.getenv("SMTP_FROM", user)
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = email
    with smtplib.SMTP(host, port, timeout=10) as server:
        server.starttls()
        server.login(user, password)
        server.sendmail(from_email, [email], msg.as_string())
    return True


def _find_nutri_chatwoot_route(db: SessionLocal, nutri_id: int) -> tuple[str | None, str | None]:
    convo = (
        db.query(Conversa)
        .join(Cliente, Cliente.id == Conversa.cliente_id)
        .filter(
            Cliente.nutricionista_id == nutri_id,
            Cliente.status == "nutri",
            Conversa.chatwoot_account_id.isnot(None),
            Conversa.chatwoot_conversation_id.isnot(None),
        )
        .order_by(Conversa.id.desc())
        .first()
    )
    if convo:
        return convo.chatwoot_account_id, convo.chatwoot_conversation_id
    cw = db.query(ChatwootAccount).filter(ChatwootAccount.nutricionista_id == nutri_id).first()
    if not cw:
        return None, None
    return cw.chatwoot_account_external_id or cw.chatwoot_account_id, None


def _notify_nutri_direct(db: SessionLocal, nutri: Nutricionista, msg: str, subject: str = "Comunicado da administração") -> str:
    account_id, conversation_id = _find_nutri_chatwoot_route(db, nutri.id)
    sent_chat = False
    if account_id and conversation_id:
        try:
            enviar_mensagens(account_id, conversation_id, [msg])
            sent_chat = True
        except Exception:
            sent_chat = False

    sent_email = _smtp_send(nutri.email, subject, msg)
    if sent_chat and sent_email:
        return f"Comunicado enviado para {nutri.nome} via Chatwoot e e-mail."
    if sent_chat:
        return f"Comunicado enviado para {nutri.nome} via Chatwoot."
    if sent_email:
        return f"Comunicado enviado para {nutri.nome} por e-mail."
    return f"Não consegui entregar para {nutri.nome}. Falta rota Chatwoot ativa e SMTP configurado."


def _asaas_info(admin_user: Nutricionista | None = None) -> str:
    cfg = load_asaas_config_from_user(admin_user) if admin_user else {}
    api_url = str(cfg.get("api_url") or (os.getenv("ASAAS_API_URL") or "https://api-sandbox.asaas.com/v3")).rstrip("/")
    key = str(cfg.get("api_key") or (os.getenv("ASAAS_API_KEY") or "")).strip()
    masked_key = f"{key[:4]}***{key[-4:]}" if len(key) >= 8 else ("configurada" if key else "não configurada")
    lines = [
        "Conta Asaas (admin):",
        f"- configurada: {'sim' if is_configured(cfg) else 'não'}",
        f"- api_url: {api_url}",
        f"- token: {masked_key}",
    ]
    try:
        if is_configured(cfg):
            balance = get_balance(config=cfg)
            lines.append(f"- saldo_disponivel: {balance.get('balance')}")
    except AsaasError as exc:
        lines.append(f"- saldo_disponivel: indisponível ({exc})")
    except Exception:
        lines.append("- saldo_disponivel: indisponível")
    return "\n".join(lines)


def _execute_action(db: SessionLocal, action_payload: dict, *, actor_nutri_id: int | None = None) -> str:
    action = action_payload.get("action", "unknown")
    if action == "system_state":
        return status_do_sistema()
    if action == "cluster_diagnosis":
        return _cluster_diag_summary(db)
    if action == "queue_report":
        grouped = db.query(WorkerJob.queue, WorkerJob.status, func.count(WorkerJob.id)).group_by(WorkerJob.queue, WorkerJob.status).all()
        if not grouped:
            return "Relatório de filas: sem jobs registrados."
        linhas = ["Relatório de filas/jobs:"]
        for queue, status, count in grouped:
            linhas.append(f"- {queue} | {status}: {count}")
        return "\n".join(linhas)
    if action == "daily_followup_now":
        return _cluster_diag_summary(db)
    if action == "daily_followup_enable":
        set_cache("adminops:daily_followup_enabled", "1", expire=60 * 60 * 24 * 365)
        return "Follow-up diário ativado. Vou enviar resumo técnico diário no canal admin."
    if action == "daily_followup_disable":
        delete_cache("adminops:daily_followup_enabled")
        return "Follow-up diário desativado."
    if action == "scale_worker":
        return _execute_scale_worker(action_payload.get("worker_service", ""), int(action_payload.get("replicas") or 0))
    if action == "backup_database":
        return _execute_backup_database()
    if action == "send_email_nutri":
        target = _find_nutri_by_query(db, action_payload.get("target_query") or "")
        if not target:
            return "Nutricionista alvo não encontrada. Informe e-mail ou nome."
        message = (action_payload.get("message_content") or "").strip()
        if not message:
            return "Mensagem do comunicado ausente."
        subject = (action_payload.get("subject") or "Comunicado da administração NutrIA-Pro").strip()
        if _smtp_send(target.email, subject, message):
            return f"E-mail enviado para {target.nome} ({target.email})."
        return f"Falha ao enviar e-mail para {target.email}. Verifique SMTP."
    if action == "send_message_nutri":
        target = _find_nutri_by_query(db, action_payload.get("target_query") or "")
        if not target:
            return "Nutricionista alvo não encontrada. Informe e-mail ou nome."
        message = (action_payload.get("message_content") or "").strip()
        if not message:
            return "Mensagem do comunicado ausente."
        return _notify_nutri_direct(db, target, message)
    if action == "broadcast_nutri_alert":
        message = (action_payload.get("message_content") or "").strip()
        if not message:
            return "Mensagem do alerta global ausente."
        nutris = db.query(Nutricionista).filter(Nutricionista.tipo_user == "nutri", Nutricionista.status == "active").all()
        if not nutris:
            return "Nenhuma nutricionista ativa para receber o alerta."
        delivered = 0
        for nutri in nutris:
            _notify_nutri_direct(db, nutri, f"[ALERTA ADMIN] {message}")
            delivered += 1
        return f"Alerta global enviado para {delivered} nutricionistas."
    if action == "register_nutri":
        nome = (action_payload.get("novo_nome") or "").strip()
        email = (action_payload.get("novo_email") or "").strip().lower()
        plano = (action_payload.get("novo_plano") or "pro").strip().lower()
        if not nome or not email:
            return "Para cadastrar nutri preciso de nome e e-mail."
        if plano not in {"trial", "basic", "pro", "enterprise"}:
            plano = "pro"
        exists = db.query(Nutricionista).filter(func.lower(Nutricionista.email) == email).first()
        if exists:
            return f"Já existe nutricionista com e-mail {email}."
        tenant, nutri, conta, senha_tmp = _provisionar_nutri_admin(
            db=db,
            nome=nome,
            email=email,
            plano_nome=plano,
        )
        enviar_email_boas_vindas_assinatura(
            email=nutri.email,
            nome=nutri.nome,
            senha_temporaria=senha_tmp,
            plano=plano,
            limite_inboxes=conta.limite_inboxes_base + conta.inboxes_extra,
        )
        return (
            f"Nutricionista cadastrada com sucesso. "
            f"nutri_id={nutri.id}, tenant_id={tenant.id}, conta_chatwoot={conta.chatwoot_account_external_id or conta.chatwoot_account_id}."
        )
    if action == "asaas_account_info":
        actor = db.query(Nutricionista).filter(Nutricionista.id == actor_nutri_id).first() if actor_nutri_id else None
        return _asaas_info(actor)
    if action == "help":
        return (
            "Comandos disponíveis: estado do servidor, diagnóstico do cluster, relatório de filas, "
            "ativar/desativar follow-up diário, subir worker, backup do banco, enviar email para nutri, "
            "enviar mensagem para nutri, alerta para todas as nutris, cadastrar nova nutri, infos da conta Asaas."
        )
    return "Comando não reconhecido. Peça estado, diagnóstico, filas, escala, backup, comunicação, cadastro ou Asaas."


def _confirmation_summary(payload: dict) -> str:
    action = payload.get("action")
    if action == "scale_worker":
        return f"Escalar worker '{payload.get('worker_service')}' para {payload.get('replicas')} réplicas."
    if action == "backup_database":
        return "Executar backup do banco de dados."
    if action == "broadcast_nutri_alert":
        return f"Enviar alerta global para todas as nutricionistas: {payload.get('message_content')}"
    if action == "register_nutri":
        return f"Cadastrar nutricionista: {payload.get('novo_nome')} <{payload.get('novo_email')}> plano {payload.get('novo_plano') or 'pro'}."
    return "Executar operação sensível."


def _handle_admin_chat_command(db: SessionLocal, payload: dict) -> str:
    account_id = str(payload.get("account_id") or "")
    conversation_id = str(payload.get("conversation_id") or "")
    message = str(payload.get("message") or "")
    if not account_id or not conversation_id:
        return "Payload admin incompleto."

    confirm_action, token = _parse_confirm_command(message)
    pending_key = _pending_key(account_id, conversation_id)
    pending_raw = _decode_cache(get_cache(pending_key))
    pending_data = _extract_json(pending_raw) if pending_raw else {}

    if confirm_action and token:
        if not pending_data or pending_data.get("token") != token:
            enviar_mensagens(account_id, conversation_id, ["Token inválido ou expirado para operação sensível."])
            return "invalid_token"
        if confirm_action == "cancel":
            delete_cache(pending_key)
            enviar_mensagens(account_id, conversation_id, ["Operação cancelada."])
            return "cancelled"
        result = _execute_action(db, pending_data.get("action_payload") or {}, actor_nutri_id=actor_nutri_id)
        delete_cache(pending_key)
        enviar_mensagens(account_id, conversation_id, [result])
        return "confirmed_executed"

    decision = _parse_admin_action(message)
    action = decision.get("action", "unknown")
    confidence = float(decision.get("confidence") or 0)

    if action in SENSITIVE_ACTIONS:
        if confidence < 0.65:
            enviar_mensagens(
                account_id,
                conversation_id,
                ["Pedido sensível com baixa confiança. Reformule com parâmetros objetivos para execução segura."],
            )
            return "low_confidence_sensitive"
        token = secrets.token_hex(3).upper()
        pending = {
            "token": token,
            "created_at": datetime.now(UTC).isoformat(),
            "expires_at": (datetime.now(UTC) + timedelta(minutes=CONFIRMATION_TTL_MINUTES)).isoformat(),
            "action_payload": decision,
        }
        set_cache(pending_key, json.dumps(pending, ensure_ascii=False), expire=CONFIRMATION_TTL_MINUTES * 60)
        resumo = _confirmation_summary(decision)
        enviar_mensagens(
            account_id,
            conversation_id,
            [f"Confirma a operação?\n{resumo}\nResponda `confirmo {token}` ou `cancelar {token}`."],
        )
        return "pending_confirmation"

    if action == "unknown" and confidence < 0.65:
        decision["action"] = "help"

    result = _execute_action(db, decision, actor_nutri_id=actor_nutri_id)
    enviar_mensagens(account_id, conversation_id, [result])
    return "executed"


def process_admin_ops(event: dict):
    event_id = event.get("event_id")
    if event_id and not set_if_not_exists(f"idempotency:{event_id}", "1", expire=3600):
        return

    db = SessionLocal()
    try:
        payload = event.get("payload", {})
        source = str(payload.get("source") or "").lower()
        comando = str(payload.get("comando", "")).lower()
        if source == "chatwoot_admin":
            payload["actor_nutri_id"] = event.get("nutricionista_id")
            _handle_admin_chat_command(db, payload)
        elif comando == "snapshot":
            notificar_admins(status_do_sistema())
        elif comando == "cluster_diagnostico":
            notificar_admins(_cluster_diag_summary(db))
        elif comando == "daily_followup":
            if _decode_cache(get_cache("adminops:daily_followup_enabled")) == "1":
                notificar_admins(_cluster_diag_summary(db))
        else:
            notificar_admins(f"[admin-ops] comando recebido: {comando or 'desconhecido'}")
        if event_id:
            update_worker_job_status(db, event_id=event_id, status="completed")
    except Exception as exc:
        if event_id:
            update_worker_job_status(
                db,
                event_id=event_id,
                status="failed",
                tentativas_increment=True,
                erro=str(exc),
            )
    finally:
        db.close()
    actor_nutri_id = int(payload.get("actor_nutri_id") or 0) or None
