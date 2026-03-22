import os
import smtplib
import time
from email.mime.text import MIMEText

import requests

from app.db import SessionLocal
from app.domain.models.nutricionista import Nutricionista
from app.domain.models.cliente import Cliente
from app.domain.models.caixa_de_entrada import CaixaDeEntrada
from app.domain.models.tenant import Tenant
from app.workers.chatwoot_message_worker import enviar_mensagem_chatwoot

ADMIN_ACCOUNT_ID = os.getenv("ADMIN_CHATWOOT_ACCOUNT_ID", "1")
ADMIN_CONVERSATION_ID = os.getenv("ADMIN_CHATWOOT_CONVERSATION_ID", "1")
ADMIN_CONTACTS = os.getenv("ADMIN_CHATWOOT_CONTACTS", "admin1,admin2").split(",")  # IDs/telefones nutri
ADMIN_ALERT_WEBHOOK_URL = os.getenv("ADMIN_ALERT_WEBHOOK_URL")
ADMIN_ALERT_EMAIL = os.getenv("ADMIN_ALERT_EMAIL")
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_FROM = os.getenv("SMTP_FROM", SMTP_USER or "noreply@nutria-pro.com")


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
    if os.getenv("TEST_ENV", "0") == "1":
        return
    # Mensagem para inbox de admin (duplicada para responsáveis)
    for c in ADMIN_CONTACTS:
        conteudo = f"[ADMIN ALERT] {mensagem}\nContato: {c}"
        enviar_mensagem_chatwoot(ADMIN_ACCOUNT_ID, ADMIN_CONVERSATION_ID, conteudo)
    if ADMIN_ALERT_WEBHOOK_URL:
        try:
            requests.post(
                ADMIN_ALERT_WEBHOOK_URL,
                json={"mensagem": mensagem, "timestamp": time.time()},
                timeout=10,
            )
        except Exception:
            pass
    if ADMIN_ALERT_EMAIL and SMTP_HOST and SMTP_USER and SMTP_PASSWORD:
        try:
            msg = MIMEText(mensagem, "plain", "utf-8")
            msg["Subject"] = "[ADMIN ALERT] NutrIA-Pro"
            msg["From"] = SMTP_FROM
            msg["To"] = ADMIN_ALERT_EMAIL
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.sendmail(SMTP_FROM, [ADMIN_ALERT_EMAIL], msg.as_string())
        except Exception:
            pass


def monitorar_periodicamente(intervalo_segundos=300):
    while True:
        try:
            metrics = status_do_sistema()
            notificar_admins(metrics)
        except Exception as ex:
            enviar_mensagem_chatwoot(ADMIN_ACCOUNT_ID, ADMIN_CONVERSATION_ID, f"Falha no monitoramento: {ex}")
        time.sleep(intervalo_segundos)
