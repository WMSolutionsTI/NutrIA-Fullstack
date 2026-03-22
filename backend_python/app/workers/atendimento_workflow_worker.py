import os
import time
import uuid
from datetime import datetime

from app.domain.models.cliente import Cliente
from app.domain.models.conversa import Conversa
from app.domain.models.nutricionista import Nutricionista
from app.workers.quebrar_enviar_mensagens_worker import enviar_mensagens
from app.workers.chatwoot_attachment_worker import enviar_arquivo_chatwoot
from app.workers.admin_monitor_worker import notificar_admins
from app.workers.minio_worker import download_object
from app.domain.models.arquivo import Arquivo
from app.db import SessionLocal
from app.services.ai_service import gerar_resposta_agente
from app.services.conversation_archive_service import archive_conversa_snapshot
from app.services.worker_job_service import update_worker_job_status


def process_file_transfer(arquivo_id, account_id, conversation_id):
    db = SessionLocal()
    try:
        arquivo = db.query(Arquivo).get(arquivo_id)
        if not arquivo:
            return {"status": "arquivo_nao_encontrado"}

        local_path = f"/tmp/{uuid.uuid4()}_{arquivo.nome}"
        if not download_object(arquivo.caminho_s3, local_path):
            return {"status": "falha_download"}

        enviado = enviar_arquivo_chatwoot(account_id, conversation_id, local_path)
        os.remove(local_path)
        return {"status": "arquivo_enviado" if enviado else "erro_envio"}
    finally:
        db.close()


def process_atendimento_workflow(payload):
    """Processa mensagem assíncrona do Chatwoot com interpretação por IA."""
    event_id = payload.get("event_id")
    event_payload = payload.get("payload", payload)
    tenant_id = payload.get("tenant_id") or event_payload.get("tenant_id")
    nutricionista_id = payload.get("nutricionista_id") or event_payload.get("nutricionista_id")
    cliente_id = payload.get("cliente_id") or event_payload.get("cliente_id")

    account_id = event_payload.get("account_id")
    conversation_id = event_payload.get("conversation_id")
    inbox_id = event_payload.get("inbox_id")
    canal = event_payload.get("canal")
    message = event_payload.get("message")
    retry_count = int(event_payload.get("retry_count") or 0)
    direct_mode_active = bool(event_payload.get("direct_mode_active"))

    arquivo_id = event_payload.get("arquivo_id")
    if arquivo_id and account_id and conversation_id:
        file_result = process_file_transfer(arquivo_id, account_id, conversation_id)
        return {"status": "arquivo_transferido", "result": file_result}

    db = SessionLocal()
    try:
        cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first() if cliente_id else None
        nutri = db.query(Nutricionista).filter(Nutricionista.id == nutricionista_id).first() if nutricionista_id else None
        if not cliente or not nutri:
            if event_id:
                update_worker_job_status(db, event_id=event_id, status="failed", erro="cliente_or_nutri_not_found")
            return {"status": "dados_incompletos"}

        if (cliente.status or "").lower() == "nutri":
            from app.workers.suporte_nutri_worker import process_comando_chatwoot

            process_comando_chatwoot(account_id, conversation_id, message or "", nutri.id, db)
            if event_id:
                update_worker_job_status(db, event_id=event_id, status="completed")
            return {"status": "nutri_comando_processado"}

        historico = (
            db.query(Conversa)
            .filter(Conversa.cliente_id == cliente.id)
            .order_by(Conversa.id.desc())
            .limit(8)
            .all()
        )
        historico_txt = "\n".join(
            [f"- ({c.modo or 'ia'}) {c.mensagem}" for c in reversed(historico) if c and c.mensagem]
        )
        contexto_nutri = nutri.contexto_ia or ""
        prompt = (
            "Atue como secretária virtual da nutricionista.\n"
            "Regras obrigatórias: manter escopo técnico, não inventar dados, não citar informações de outros clientes/contas e pedir confirmação se faltar contexto crítico.\n"
            f"Cliente: {cliente.nome} | Status: {cliente.status}\n"
            f"Canal: {canal or 'desconhecido'} | Inbox: {inbox_id or '-'}\n"
            f"Contexto da nutri: {contexto_nutri}\n"
            f"Histórico recente:\n{historico_txt}\n"
            f"Mensagem atual: {message}\n"
            "Responda de forma natural, objetiva e útil."
        )
        resposta = gerar_resposta_agente("secretaria", prompt, contexto=contexto_nutri, model="gpt-4o-mini", temperature=0.4)

        if account_id and conversation_id:
            enviar_mensagens(account_id, conversation_id, [resposta])

        conversa_resp = Conversa(
            cliente_id=cliente.id,
            nutricionista_id=nutri.id,
            caixa_id=None,
            chatwoot_account_id=str(account_id) if account_id is not None else None,
            chatwoot_inbox_id=str(inbox_id) if inbox_id is not None else None,
            canal_origem=canal,
            chatwoot_conversation_id=str(conversation_id) if conversation_id is not None else None,
            mensagem=resposta,
            data=datetime.utcnow(),
            modo="ia" if not direct_mode_active else "direto",
            contexto_ia=contexto_nutri,
            em_conversa_direta=direct_mode_active,
        )
        db.add(conversa_resp)
        db.commit()
        db.refresh(conversa_resp)
        archive_conversa_snapshot(db, conversa=conversa_resp, tenant_id=tenant_id)

        if event_id:
            update_worker_job_status(db, event_id=event_id, status="completed")
        return {"status": "ok", "message": resposta}
    except Exception as ex:
        if account_id and conversation_id:
            enviar_mensagens(
                account_id,
                conversation_id,
                ["Estou com instabilidade momentânea, mas já estou tentando novamente em instantes."],
            )
        if retry_count < 2 and tenant_id and nutricionista_id and cliente_id:
            from app.services.event_bus import build_event_payload, publish_event
            from app.services.worker_job_service import create_worker_job

            time.sleep(min(2 ** retry_count, 4))
            retry_event = build_event_payload(
                queue_tipo="chatwoot_message_received",
                tenant_id=int(tenant_id),
                nutricionista_id=int(nutricionista_id),
                cliente_id=int(cliente_id),
                payload={
                    **event_payload,
                    "retry_count": retry_count + 1,
                },
            )
            publish_event("queue.atendimento", retry_event)
            create_worker_job(
                db,
                event_id=retry_event["event_id"],
                queue="queue.atendimento",
                tipo="chatwoot_message_received_retry",
                tenant_id=int(tenant_id),
                nutricionista_id=int(nutricionista_id),
                cliente_id=int(cliente_id),
                payload=retry_event,
            )
            if event_id:
                update_worker_job_status(db, event_id=event_id, status="failed", tentativas_increment=True, erro=str(ex))
            return {"status": "retry_enqueued", "erro": str(ex)}

        notificar_admins(f"Falha no worker IA atendimento: {ex}")
        if event_id:
            update_worker_job_status(db, event_id=event_id, status="failed", tentativas_increment=True, erro=str(ex))
        return {"status": "failed", "erro": str(ex)}
    finally:
        db.close()
