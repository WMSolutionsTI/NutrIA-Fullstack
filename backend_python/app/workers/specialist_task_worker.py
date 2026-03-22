from app.db import SessionLocal
from app.services.ai_service import gerar_resposta_agente
from app.services.worker_job_service import update_worker_job_status
from app.workers.admin_monitor_worker import notificar_admins
from app.workers.quebrar_enviar_mensagens_worker import enviar_mensagens


SPECIALIST_AGENT_MAP = {
    "agenda": "secretaria",
    "financeiro": "agente_financeiro",
    "plano": "elaborador_plano",
    "atendimento": "secretaria",
    "operacoes": "suporte_tecnico",
}


def process_specialist_task(event: dict):
    event_id = event.get("event_id")
    payload = event.get("payload", {})
    specialist = str(payload.get("specialist") or "atendimento").lower()
    objective = str(payload.get("objective") or "").strip()
    original_message = str(payload.get("original_message") or "").strip()
    contexto_nutri = str(payload.get("contexto_nutri") or "").strip()
    account_id = payload.get("account_id")
    conversation_id = payload.get("conversation_id")

    db = SessionLocal()
    try:
        assunto = SPECIALIST_AGENT_MAP.get(specialist, "consultor")
        prompt = (
            "Você é um agente especialista de apoio à secretária de nutricionista.\n"
            "Regras: cumprir estritamente sua especialidade, não inventar dados, não fornecer informações de outros clientes/tenants e não extrapolar permissões.\n"
            f"Especialidade: {specialist}\n"
            f"Objetivo: {objective}\n"
            f"Pedido original: {original_message}\n"
            f"Contexto da nutri: {contexto_nutri}\n"
            "Responda em português com instruções práticas e, se possível, já com texto pronto para envio."
        )
        resposta = gerar_resposta_agente(assunto, prompt, contexto=contexto_nutri, model="gpt-4o-mini", temperature=0.3)
        if account_id and conversation_id:
            enviar_mensagens(account_id, conversation_id, [resposta])
        if event_id:
            update_worker_job_status(db, event_id=event_id, status="completed")
    except Exception as exc:
        if account_id and conversation_id:
            enviar_mensagens(
                account_id,
                conversation_id,
                ["Tive uma falha ao consultar o especialista. Vou tentar novamente e te atualizo já."],
            )
        if event_id:
            update_worker_job_status(db, event_id=event_id, status="failed", tentativas_increment=True, erro=str(exc))
        notificar_admins(f"Falha no specialist_task_worker: {exc}")
    finally:
        db.close()
