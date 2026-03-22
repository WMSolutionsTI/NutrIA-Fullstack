from googleapiclient.discovery import build
from google.oauth2 import service_account
import os

SCOPES = ['https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_CALENDAR_CREDENTIALS", "service_account.json")

# Função para buscar janelas disponíveis

def buscar_janelas_disponiveis(calendar_id, start, end):
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('calendar', 'v3', credentials=creds)
    events_result = service.events().list(calendarId=calendar_id, timeMin=start, timeMax=end, singleEvents=True, orderBy='startTime').execute()
    events = events_result.get('items', [])
    janelas = []
    for event in events:
        janelas.append({
            'inicio': event['start'].get('dateTime'),
            'fim': event['end'].get('dateTime'),
            'descricao': event.get('summary', '')
        })
    return janelas

    # Worker pode ser chamado por fila para buscar janelas disponíveis