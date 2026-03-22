from datetime import UTC, datetime, timedelta
import json

from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.domain.models.avanco import Avanco
from app.domain.models.cliente import Cliente
from app.domain.models.conversa import Conversa
from app.domain.models.nutricionista import Nutricionista
from app.domain.models.plano_alimentar import PlanoAlimentar
from app.services.anamnese_service import send_anamnese_followup_tick
from app.services.worker_job_service import update_worker_job_status
from app.workers.admin_monitor_worker import notificar_admins
from app.workers.quebrar_enviar_mensagens_worker import enviar_mensagens
from app.workers.redis_worker import set_if_not_exists

MEAL_DEFAULT_HOURS = {
    "cafe": "08:00",
    "cafe_da_manha": "08:00",
    "almoco": "12:00",
    "lanche": "16:00",
    "jantar": "19:00",
    "ceia": "21:00",
}


def _idempotent_once(key: str, expire: int = 60 * 60 * 24) -> bool:
    try:
        return bool(set_if_not_exists(key, "1", expire=expire))
    except Exception:
        return True


def _parse_refeicoes(refeicoes_raw: str | None) -> list[dict]:
    if not refeicoes_raw:
        return []
    try:
        parsed = json.loads(refeicoes_raw)
    except Exception:
        return []
    meals: list[dict] = []
    if isinstance(parsed, list):
        for idx, item in enumerate(parsed):
            if isinstance(item, dict):
                nome = str(item.get("nome") or item.get("refeicao") or f"refeicao_{idx+1}")
                horario = str(item.get("horario") or "").strip()
                if not horario and nome:
                    horario = MEAL_DEFAULT_HOURS.get(nome.strip().lower(), "")
                if horario:
                    meals.append({"nome": nome, "horario": horario})
            elif isinstance(item, str):
                nome = item.strip()
                horario = MEAL_DEFAULT_HOURS.get(nome.lower(), "")
                if horario:
                    meals.append({"nome": nome, "horario": horario})
    return meals


def _latest_client_chat_route(db: Session, cliente_id: int) -> tuple[str | None, str | None]:
    conversa = (
        db.query(Conversa)
        .filter(
            Conversa.cliente_id == cliente_id,
            Conversa.chatwoot_account_id.isnot(None),
            Conversa.chatwoot_conversation_id.isnot(None),
        )
        .order_by(Conversa.id.desc())
        .first()
    )
    if not conversa:
        return None, None
    return conversa.chatwoot_account_id, conversa.chatwoot_conversation_id


def _parse_hhmm(base_day: datetime, hhmm: str) -> datetime | None:
    try:
        hh, mm = hhmm.split(":", 1)
        return base_day.replace(hour=int(hh), minute=int(mm), second=0, microsecond=0)
    except Exception:
        return None


def _register_avanco(db: Session, *, cliente_id: int, nutri_id: int, descricao: str) -> None:
    avanco = Avanco(
        cliente_id=cliente_id,
        nutricionista_id=nutri_id,
        data=datetime.utcnow(),
        descricao=descricao,
        status="concluido",
    )
    db.add(avanco)
    db.commit()


def _send_meal_followup_tick(db: Session, payload: dict) -> dict:
    now_utc = datetime.now(UTC).replace(tzinfo=None)
    tenant_id = payload.get("tenant_id")
    nutri_id = payload.get("nutricionista_id")
    cliente_id = payload.get("cliente_id")

    q = db.query(PlanoAlimentar).filter(PlanoAlimentar.status == "ativo")
    if cliente_id:
        q = q.filter(PlanoAlimentar.cliente_id == int(cliente_id))
    elif nutri_id:
        q = q.filter(PlanoAlimentar.nutricionista_id == int(nutri_id))
    elif tenant_id:
        q = q.join(Cliente, Cliente.id == PlanoAlimentar.cliente_id).filter(Cliente.nutricionista_id.isnot(None))

    planos = q.all()
    sent_count = 0
    for plano in planos:
        cliente = db.query(Cliente).filter(Cliente.id == plano.cliente_id).first()
        if not cliente:
            continue
        account_id, conversation_id = _latest_client_chat_route(db, cliente.id)
        if not account_id or not conversation_id:
            continue

        refeições = _parse_refeicoes(plano.refeicoes)
        if not refeições:
            continue

        for item in refeições:
            meal_name = item["nome"]
            meal_time = _parse_hhmm(now_utc, item["horario"])
            if not meal_time:
                continue
            pre_time = meal_time - timedelta(minutes=60)
            post_time = meal_time + timedelta(minutes=60)

            if pre_time <= now_utc <= pre_time + timedelta(minutes=10):
                key = f"meal:pre:{cliente.id}:{now_utc.date().isoformat()}:{meal_name}"
                if _idempotent_once(key):
                    text = (
                        f"Oi {cliente.nome}, faltam ~60 min para sua refeição ({meal_name}). "
                        "Você vai conseguir cumprir como planejado? "
                        "Posso ajudar com substituições equivalentes, dicas de receita e explicar nutrientes/calorias."
                    )
                    enviar_mensagens(account_id, conversation_id, [text])
                    _register_avanco(
                        db,
                        cliente_id=cliente.id,
                        nutri_id=plano.nutricionista_id,
                        descricao=f"[MEAL_PRE] Suporte enviado 60min antes da refeição {meal_name}.",
                    )
                    sent_count += 1

            if post_time <= now_utc <= post_time + timedelta(minutes=10):
                key = f"meal:post:{cliente.id}:{now_utc.date().isoformat()}:{meal_name}"
                if _idempotent_once(key):
                    text = (
                        f"Passando para confirmar sua refeição ({meal_name}). "
                        "Conseguiu executar conforme o plano? Houve substituição ou intercorrência? "
                        "Se quiser, pode enviar foto do prato para análise."
                    )
                    enviar_mensagens(account_id, conversation_id, [text])
                    _register_avanco(
                        db,
                        cliente_id=cliente.id,
                        nutri_id=plano.nutricionista_id,
                        descricao=f"[MEAL_POST] Follow-up enviado 60min após a refeição {meal_name}.",
                    )
                    sent_count += 1

        # lembrete de água e hábitos (periodicamente)
        if now_utc.hour in {8, 12, 16, 20} and now_utc.minute <= 10:
            key = f"habit:water:{cliente.id}:{now_utc.date().isoformat()}:{now_utc.hour}"
            if _idempotent_once(key, expire=60 * 60 * 48):
                enviar_mensagens(
                    account_id,
                    conversation_id,
                    ["Lembrete rápido: mantenha hidratação adequada hoje e foque em hábitos consistentes."],
                )
                _register_avanco(
                    db,
                    cliente_id=cliente.id,
                    nutri_id=plano.nutricionista_id,
                    descricao="[HABIT] Lembrete de hidratação e hábitos saudáveis enviado.",
                )
                sent_count += 1

    return {"status": "ok", "sent": sent_count}


def process_notification_event(event: dict):
    event_id = event.get("event_id")
    payload = event.get("payload", {})
    tipo = str(payload.get("tipo") or event.get("tipo") or "").lower()

    db = SessionLocal()
    try:
        if tipo == "meal_followup_tick":
            _send_meal_followup_tick(db, payload)
        if tipo == "anamnese_followup_tick":
            send_anamnese_followup_tick(db, payload)
        if event_id:
            update_worker_job_status(db, event_id=event_id, status="completed")
    except Exception as exc:
        if event_id:
            update_worker_job_status(db, event_id=event_id, status="failed", tentativas_increment=True, erro=str(exc))
        notificar_admins(f"Falha no meal_support_worker: {exc}")
    finally:
        db.close()
