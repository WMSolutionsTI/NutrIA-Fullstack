import requests
import os
import psycopg2
from googleapiclient.discovery import build
from google.oauth2 import service_account

CHATWOOT_URL = os.getenv("CHATWOOT_URL", "http://chatwoot:3000")
CHATWOOT_API_KEY = os.getenv("CHATWOOT_API_KEY", "your_api_key")
DATABASE_URL = os.getenv("DATABASE_URL")
SCOPES = ['https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_CALENDAR_CREDENTIALS", "service_account.json")

# Função para remover evento Google Calendar
def remover_evento_google(calendar_id, google_event_id):
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('calendar', 'v3', credentials=creds)
    service.events().delete(calendarId=calendar_id, eventId=google_event_id).execute()
    print(f"Evento Google {google_event_id} removido da agenda {calendar_id}")

# Função para desmarcar agendamento e enviar alerta

def desmarcar_agendamento(id_agenda, account_id, conversation_id, mensagem_alerta, calendar_id=None, google_event_id=None):
    # Remove agendamento do banco
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("DELETE FROM agenda_nutricionista WHERE id_agenda=%s", (id_agenda,))
    conn.commit()
    cur.close()
    conn.close()
    # Remove evento Google Calendar se informado
    if calendar_id and google_event_id:
        remover_evento_google(calendar_id, google_event_id)
    # Envia alerta via Chatwoot
    url = f"{CHATWOOT_URL}/api/v1/accounts/{account_id}/conversations/{conversation_id}/messages"
    headers = {"api_access_token": CHATWOOT_API_KEY}
    data = {"content": mensagem_alerta}
    from app.core.logging import logger
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        logger.info("Alerta enviado", extra={"mensagem_alerta": mensagem_alerta})
        return True
    else:
        logger.error("Erro ao enviar alerta", extra={"error": response.text})
        return False

# Exemplo de uso:
if __name__ == "__main__":
    id_agenda = 1
    account_id = 1
    conversation_id = 12345
    mensagem_alerta = "Seu agendamento foi desmarcado."
    desmarcar_agendamento(id_agenda, account_id, conversation_id, mensagem_alerta)