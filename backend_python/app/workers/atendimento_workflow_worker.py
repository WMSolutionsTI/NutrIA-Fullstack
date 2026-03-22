import os
import time
import uuid
import json
import re
from datetime import datetime

from app.domain.models.cliente import Cliente
from app.domain.models.conversa import Conversa
from app.domain.models.contabilidade import Contabilidade
from app.domain.models.avanco import Avanco
from app.domain.models.agenda_evento import AgendaEvento
from app.domain.models.nutricionista import Nutricionista
from app.domain.models.pagamento import Pagamento
from app.workers.quebrar_enviar_mensagens_worker import enviar_mensagens
from app.workers.chatwoot_attachment_worker import enviar_arquivo_chatwoot
from app.workers.minio_worker import download_object
from app.domain.models.arquivo import Arquivo
from app.db import SessionLocal
from app.services.asaas_service import (
    AsaasError,
    create_customer,
    create_payment,
    is_configured,
    load_asaas_config_from_user,
)
from app.services.ai_service import gerar_resposta_agente
from app.services.anamnese_service import ensure_anamnese_workflow_for_cliente, process_anamnese_message
from app.services.conversation_archive_service import archive_conversa_snapshot
from app.services.worker_job_service import update_worker_job_status
from app.utils.text_normalize import normalize_pt_text


def _extract_json(texto: str) -> dict:
    if not texto:
        return {}
    texto = texto.strip()
    try:
        payload = json.loads(texto)
        return payload if isinstance(payload, dict) else {}
    except Exception:
        pass
    match = re.search(r"\{.*\}", texto, flags=re.DOTALL)
    if not match:
        return {}
    try:
        payload = json.loads(match.group(0))
        return payload if isinstance(payload, dict) else {}
    except Exception:
        return {}


def _normalize_phone(raw: str | None) -> str | None:
    if not raw:
        return None
    digits = "".join(ch for ch in str(raw) if ch.isdigit())
    if len(digits) < 10:
        return None
    if len(digits) == 11 and digits.startswith("0"):
        digits = digits[1:]
    return f"+{digits}"


def _load_setup_text(nutri: Nutricionista) -> str:
    try:
        metadata = json.loads(nutri.permissoes or "{}")
    except Exception:
        return ""
    setup = metadata.get("setup", {})
    if not isinstance(setup, dict):
        return ""
    return str(setup.get("pacotes_atendimento") or "")


def _resolve_value_from_setup(setup_text: str, months: int | None) -> float | None:
    if not setup_text:
        return None
    normalized = setup_text.lower()
    if months and str(months) in normalized:
        pattern = re.compile(rf"{months}\s*(?:mes|m[eê]s|meses).*?(?:r\$\s*)?(\d+[.,]?\d*)", re.IGNORECASE | re.DOTALL)
        m = pattern.search(setup_text)
        if m:
            return float(m.group(1).replace(".", "").replace(",", "."))
    generic = re.search(r"(?:r\$\s*)?(\d+[.,]?\d*)", setup_text, flags=re.IGNORECASE)
    if generic:
        return float(generic.group(1).replace(".", "").replace(",", "."))
    return None


def _parse_cliente_metadata(cliente: Cliente) -> dict:
    try:
        metadata = json.loads(cliente.historico or "{}")
        if isinstance(metadata, dict):
            return metadata
    except Exception:
        pass
    return {"legacy_historico": cliente.historico} if cliente.historico else {}


def _save_cliente_metadata(cliente: Cliente, metadata: dict) -> None:
    cliente.historico = json.dumps(metadata, ensure_ascii=False)


def _planner_comercial(
    *,
    message: str,
    historico_txt: str,
    contexto_nutri: str,
    setup_text: str,
) -> dict:
    prompt = f"""
Você é orquestrador comercial da secretária de uma nutricionista.
Responda SOMENTE JSON válido.

Schema:
{{
  "action": "create_payment_link" | "answer_payment_options" | "ask_clarification" | "fallback",
  "package_months": 0,
  "billing_type": "PIX|BOLETO|CREDIT_CARD|UNKNOWN",
  "value_brl": 0.0,
  "customer_email": "string ou vazio",
  "customer_cpf_cnpj": "string ou vazio",
  "confidence": 0.0,
  "reason": "string curta"
}}

Regras:
- Use "fallback" se a mensagem não for comercial.
- Use "answer_payment_options" quando cliente pedir formas de pagamento ou preço sem escolher método final.
- Use "create_payment_link" quando cliente já quer fechar e houver dados suficientes.
- Nunca invente preço. Se preço não estiver explícito, deixe value_brl=0.

Contexto da nutricionista:
{contexto_nutri or "-"}

Pacotes cadastrados:
{setup_text or "-"}

Histórico recente:
{historico_txt or "-"}

Mensagem atual:
{message or "-"}
"""
    raw = gerar_resposta_agente("agente_financeiro", prompt, contexto=contexto_nutri, model="gpt-4o-mini", temperature=0.1)
    parsed = _extract_json(raw)
    action = str(parsed.get("action") or "fallback").strip()
    if action not in {"create_payment_link", "answer_payment_options", "ask_clarification", "fallback"}:
        action = "fallback"
    return {
        "action": action,
        "package_months": int(parsed.get("package_months") or 0),
        "billing_type": str(parsed.get("billing_type") or "UNKNOWN").upper().strip(),
        "value_brl": float(parsed.get("value_brl") or 0),
        "customer_email": str(parsed.get("customer_email") or "").strip(),
        "customer_cpf_cnpj": str(parsed.get("customer_cpf_cnpj") or "").strip(),
        "confidence": float(parsed.get("confidence") or 0),
        "reason": str(parsed.get("reason") or "").strip(),
    }


def _human_billing_types() -> str:
    return "PIX, boleto bancário e cartão de crédito."


def _next_scheduled_consulta(db, *, cliente_id: int, nutri_id: int) -> AgendaEvento | None:
    now = datetime.utcnow()
    return (
        db.query(AgendaEvento)
        .filter(
            AgendaEvento.cliente_id == cliente_id,
            AgendaEvento.nutricionista_id == nutri_id,
            AgendaEvento.status == "agendado",
            AgendaEvento.inicio_em > now,
        )
        .order_by(AgendaEvento.inicio_em.asc())
        .first()
    )


def _create_checkout_for_client(
    *,
    db,
    event_id: str | None,
    nutri: Nutricionista,
    cliente: Cliente,
    account_id: str,
    conversation_id: str,
    planner: dict,
    setup_text: str,
) -> bool:
    asaas_cfg = load_asaas_config_from_user(nutri)
    consulta = _next_scheduled_consulta(db, cliente_id=cliente.id, nutri_id=nutri.id)
    if not consulta:
        enviar_mensagens(
            account_id,
            conversation_id,
            [
                "Antes do pagamento, preciso primeiro agendar sua consulta. "
                "Me informe o melhor dia e horário para eu registrar o agendamento."
            ],
        )
        return True

    if not is_configured(asaas_cfg):
        enviar_mensagens(
            account_id,
            conversation_id,
            [
                "Para gerar sua cobrança, a integração financeira da nutricionista ainda não foi configurada. "
                "Vou sinalizar a equipe dela para concluir a configuração e te retornar em seguida."
            ],
        )
        return True

    billing_type = planner.get("billing_type") or "UNKNOWN"
    if billing_type not in {"PIX", "BOLETO", "CREDIT_CARD"}:
        enviar_mensagens(
            account_id,
            conversation_id,
            [f"As formas de pagamento são {_human_billing_types()} Qual você prefere para eu gerar o link?"],
        )
        return True

    value = float(planner.get("value_brl") or 0)
    if value <= 0:
        value = float(_resolve_value_from_setup(setup_text, planner.get("package_months")) or 0)
    if value <= 0:
        enviar_mensagens(
            account_id,
            conversation_id,
            [
                "Consigo gerar o link agora, mas preciso confirmar o valor do pacote selecionado. "
                "Me informe o pacote exato (ex.: 3 meses) e eu sigo com o checkout."
            ],
        )
        return True

    metadata = _parse_cliente_metadata(cliente)
    asaas_customer_id = str(metadata.get("asaas_customer_id") or "").strip()
    try:
        if not asaas_customer_id:
            customer = create_customer(
                nome=cliente.nome,
                email=planner.get("customer_email") or None,
                cpf_cnpj=planner.get("customer_cpf_cnpj") or None,
                mobile_phone=_normalize_phone(cliente.contato_chatwoot),
                external_reference=f"tenant:{nutri.tenant_id}:cliente:{cliente.id}",
                config=asaas_cfg,
            )
            asaas_customer_id = str(customer.get("id") or "").strip()
            if not asaas_customer_id:
                raise AsaasError("Não recebi customer_id do Asaas.")
            metadata["asaas_customer_id"] = asaas_customer_id
            _save_cliente_metadata(cliente, metadata)
            db.add(cliente)

        external_reference = f"chatwoot:{account_id}:{conversation_id}"
        package_months = int(planner.get("package_months") or 0)
        description = (
            f"Pacote nutricional {package_months} meses"
            if package_months > 0
            else "Pacote nutricional"
        )
        payment = create_payment(
            customer_id=asaas_customer_id,
            value=value,
            billing_type=billing_type,
            description=description,
            external_reference=external_reference,
            due_date=consulta.inicio_em.date().isoformat(),
            config=asaas_cfg,
        )
        asaas_payment_id = str(payment.get("id") or "").strip()
        if not asaas_payment_id:
            raise AsaasError("Não recebi payment_id do Asaas.")

        link = (
            payment.get("invoiceUrl")
            or payment.get("bankSlipUrl")
            or payment.get("transactionReceiptUrl")
            or payment.get("pixQrCode")
            or ""
        )
        due_date = payment.get("dueDate")
        due_date_dt = None
        if isinstance(due_date, str) and due_date:
            try:
                due_date_dt = datetime.fromisoformat(due_date)
            except Exception:
                due_date_dt = datetime.utcnow()

        registro = Pagamento(
            cliente_id=cliente.id,
            nutricionista_id=nutri.id,
            valor=value,
            metodo=billing_type.lower(),
            status="pendente",
            data_vencimento=due_date_dt,
            referencia=asaas_payment_id,
        )
        db.add(registro)

        contab = Contabilidade(
            tipo="pagamento_assas",
            valor=int(round(value)),
            descricao=f"Cobrança checkout cliente #{cliente.id} ({description})",
            data=datetime.utcnow(),
            status="pendente",
            tenant_id=nutri.tenant_id,
            cliente_id=cliente.id,
            assas_id=asaas_payment_id,
        )
        db.add(contab)
        db.commit()
        db.refresh(registro)

        # Anamnese inicia após consulta agendada + cobrança criada (mesmo pendente).
        ensure_anamnese_workflow_for_cliente(
            db,
            cliente_id=cliente.id,
            nutricionista_id=nutri.id,
            tenant_id=nutri.tenant_id,
            pagamento_id=registro.id,
            origin="billing_created",
        )

        message_lines = [
            f"Perfeito, já gerei seu link de pagamento ({billing_type}) para o pacote solicitado.",
            f"Valor: R$ {value:.2f}",
            f"Vencimento: {consulta.inicio_em.strftime('%Y-%m-%d')}",
        ]
        if link:
            message_lines.append(f"Link: {link}")
        message_lines.append("A anamnese pré-consulta já está liberada e pode ser concluída em etapas.")
        enviar_mensagens(account_id, conversation_id, ["\n".join(message_lines)])
        return True
    except AsaasError as exc:
        db.rollback()
        enviar_mensagens(
            account_id,
            conversation_id,
            [
                "Tive uma instabilidade para gerar o checkout agora. "
                "Já registrei internamente e vou te enviar o link em seguida."
            ],
        )
        return True


def _try_handle_commercial_flow(
    *,
    db,
    event_id: str | None,
    nutri: Nutricionista,
    cliente: Cliente,
    account_id: str,
    conversation_id: str,
    message: str,
    historico_txt: str,
) -> bool:
    contexto_nutri = nutri.contexto_ia or ""
    setup_text = _load_setup_text(nutri)
    planner = _planner_comercial(
        message=message or "",
        historico_txt=historico_txt,
        contexto_nutri=contexto_nutri,
        setup_text=setup_text,
    )
    action = planner.get("action") or "fallback"
    confidence = float(planner.get("confidence") or 0)

    if action == "fallback":
        return False

    consulta = _next_scheduled_consulta(db, cliente_id=cliente.id, nutri_id=nutri.id)
    if not consulta:
        enviar_mensagens(
            account_id,
            conversation_id,
            [
                "Para seguir com formas de pagamento, preciso que a consulta esteja agendada primeiro. "
                "Me passe dia e horário desejados."
            ],
        )
        return True

    if confidence < 0.65:
        enviar_mensagens(
            account_id,
            conversation_id,
            [
                "Posso te ajudar com isso. Para avançar com segurança, me confirme o pacote desejado e "
                "a forma de pagamento (PIX, boleto ou cartão)."
            ],
        )
        return True

    if action == "answer_payment_options":
        package_months = int(planner.get("package_months") or 0)
        value = float(planner.get("value_brl") or 0)
        if value <= 0:
            value = float(_resolve_value_from_setup(setup_text, package_months) or 0)
        prefix = "Perfeito. "
        if package_months > 0 and value > 0:
            prefix = f"Perfeito. Para o pacote de {package_months} meses, o valor é R$ {value:.2f}. "
        elif package_months > 0:
            prefix = f"Perfeito. Para o pacote de {package_months} meses, "
        enviar_mensagens(
            account_id,
            conversation_id,
            [
                f"{prefix}as formas de pagamento são {_human_billing_types()} "
                "Se quiser, já gero agora seu link de checkout na forma que preferir."
            ],
        )
        return True

    if action in {"create_payment_link", "ask_clarification"}:
        if action == "ask_clarification":
            enviar_mensagens(
                account_id,
                conversation_id,
                [f"Para gerar seu pagamento, me confirme a forma escolhida: {_human_billing_types()}"],
            )
            return True
        return _create_checkout_for_client(
            db=db,
            event_id=event_id,
            nutri=nutri,
            cliente=cliente,
            account_id=account_id,
            conversation_id=conversation_id,
            planner=planner,
            setup_text=setup_text,
        )

    return False


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


def _registrar_feedback_refeicao(db, *, cliente_id: int, nutri_id: int, message: str) -> None:
    text = normalize_pt_text(message)
    keywords = [
        "refeicao",
        "prato",
        "caloria",
        "nutriente",
        "substituicao",
        "dieta",
        "plano alimentar",
        "comi",
        "foto",
    ]
    if not any(k in text for k in keywords):
        return
    avanco = Avanco(
        cliente_id=cliente_id,
        nutricionista_id=nutri_id,
        data=datetime.utcnow(),
        descricao=f"[MEAL_FEEDBACK] {message}",
        status="concluido",
    )
    db.add(avanco)
    db.commit()


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
    attachments_count = int(event_payload.get("attachments_count") or 0)
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

        if message:
            _registrar_feedback_refeicao(
                db,
                cliente_id=cliente.id,
                nutri_id=nutri.id,
                message=message,
            )

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
        comercial_handled = _try_handle_commercial_flow(
            db=db,
            event_id=event_id,
            nutri=nutri,
            cliente=cliente,
            account_id=account_id,
            conversation_id=conversation_id,
            message=message or "",
            historico_txt=historico_txt,
        )
        if comercial_handled:
            if event_id:
                update_worker_job_status(db, event_id=event_id, status="completed")
            return {"status": "ok", "message": "commercial_flow_handled"}

        message_for_anamnese = message or ""
        if attachments_count > 0:
            message_for_anamnese = f"{message_for_anamnese} [cliente_enviou_foto]"
        anamnese_handled, anamnese_reply = process_anamnese_message(
            db,
            cliente=cliente,
            nutri=nutri,
            message=message_for_anamnese,
        )
        if anamnese_handled and anamnese_reply:
            if account_id and conversation_id:
                enviar_mensagens(account_id, conversation_id, [anamnese_reply])
            conversa_resp = Conversa(
                cliente_id=cliente.id,
                nutricionista_id=nutri.id,
                caixa_id=None,
                chatwoot_account_id=str(account_id) if account_id is not None else None,
                chatwoot_inbox_id=str(inbox_id) if inbox_id is not None else None,
                canal_origem=canal,
                chatwoot_conversation_id=str(conversation_id) if conversation_id is not None else None,
                mensagem=anamnese_reply,
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
            return {"status": "ok", "message": "anamnese_flow_handled"}

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

        if event_id:
            update_worker_job_status(db, event_id=event_id, status="failed", tentativas_increment=True, erro=str(ex))
        return {"status": "failed", "erro": str(ex)}
    finally:
        db.close()
