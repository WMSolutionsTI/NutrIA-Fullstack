from googleapiclient.discovery import build
from google.oauth2 import service_account
import os
import psycopg2

SCOPES = ['https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_CALENDAR_CREDENTIALS", "service_account.json")
DATABASE_URL = os.getenv("DATABASE_URL")

# Função para criar evento no Google Calendar e atualizar agenda local

def criar_evento(calendar_id, inicio, fim, titulo, descricao, id_agenda):
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('calendar', 'v3', credentials=creds)
    event = {
        'summary': titulo,
        'description': descricao,
        'start': {'dateTime': inicio, 'timeZone': 'America/Sao_Paulo'},
        'end': {'dateTime': fim, 'timeZone': 'America/Sao_Paulo'}
    }
    created_event = service.events().insert(calendarId=calendar_id, body=event).execute()
    # Atualizar agenda local (painel)
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("INSERT INTO agenda_nutricionista (id_agenda, inicio, fim, titulo, descricao, google_event_id) VALUES (%s, %s, %s, %s, %s, %s)",
                (id_agenda, inicio, fim, titulo, descricao, created_event['id']))
    conn.commit()
    cur.close()
    conn.close()
    return created_event

    # Worker pode ser chamado por fila para criar evento no Google Calendar e atualizar agenda local
    evento = criar_evento(calendar_id, inicio, fim, titulo, descricao, id_agenda)
    print("Evento criado:", evento)