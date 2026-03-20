import os
import time
from app.db import SessionLocal
from app.domain.models.nutricionista import Nutricionista
from app.domain.models.cliente import Cliente
from app.domain.models.caixa_de_entrada import CaixaDeEntrada
from app.domain.models.tenant import Tenant
from app.workers.chatwoot_message_worker import enviar_mensagem_chatwoot

ADMIN_ACCOUNT_ID = os.getenv("ADMIN_CHATWOOT_ACCOUNT_ID", "1")
ADMIN_CONVERSATION_ID = os.getenv("ADMIN_CHATWOOT_CONVERSATION_ID", "1")
ADMIN_CONTACTS = os.getenv("ADMIN_CHATWOOT_CONTACTS", "admin1,admin2").split(",")  # IDs/telefones nutri


def coletar_metricas():
    db = SessionLocal()
    try:
        total_nutris = db.query(Nutricionista).count()
        total_clientes = db.query(Cliente).count()
        total_inboxes = db.query(CaixaDeEntrada).count()
        total_tenants = db.query(Tenant).count()
        return {
            "total_nutricionistas": total_nutris,
            "total_clientes": total_clientes,
            "total_inboxes": total_inboxes,
            "total_tenants": total_tenants,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
    finally:
        db.close()


def status_do_sistema():
    metrics = coletar_metricas()
    return "SaaS Metrics:\n" + "\n".join([f"{k}: {v}" for k, v in metrics.items()])


def notificar_admins(mensagem):
    # Mensagem para inbox de admin (duplicada para responsáveis)
    for c in ADMIN_CONTACTS:
        conteudo = f"[ADMIN ALERT] {mensagem}\nContato: {c}"
        enviar_mensagem_chatwoot(ADMIN_ACCOUNT_ID, ADMIN_CONVERSATION_ID, conteudo)


def monitorar_periodicamente(intervalo_segundos=300):
    while True:
        try:
            metrics = status_do_sistema()
            notificar_admins(metrics)
        except Exception as ex:
            enviar_mensagem_chatwoot(ADMIN_ACCOUNT_ID, ADMIN_CONVERSATION_ID, f"Falha no monitoramento: {ex}")
        time.sleep(intervalo_segundos)
