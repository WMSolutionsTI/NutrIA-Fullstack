"""
Worker: Agente de Lembretes de Agendamento
Automatiza o envio de lembretes de consultas agendadas para pacientes, solicitando confirmação de presença e informando status de pagamento.
- Busca eventos futuros nas agendas configuradas
- Verifica cadência de lembretes (ex: 24h, 1h antes)
- Gera mensagem personalizada via IA (prompt SOP)
- Envia mensagem via Chatwoot
- Marca lembrete como enviado
- Integra com workflow Buscar ou criar contato + conversa
"""
import os
import datetime
import requests
from backend.shared.events import publish_event
from backend.shared.models import get_db_session, Agenda, Evento, Contato, Conversa

CHATWOOT_URL = os.getenv("CHATWOOT_URL")
CHATWOOT_ACCOUNT_ID = os.getenv("CHATWOOT_ACCOUNT_ID")
CHATWOOT_INBOX_ID = os.getenv("CHATWOOT_INBOX_ID")
CADENCIA_LEMBRETES = [24, 1]  # Horas antes do evento

# TODO: Carregar agendas configuradas dinamicamente
AGENDAS_IDS = os.getenv("AGENDAS_IDS", "").split(",")

# TODO: Integrar com Google Calendar API (ou agenda local)
def buscar_eventos_futuros(agenda_id):
    # Exemplo: buscar eventos próximos 7 dias
    session = get_db_session()
    agora = datetime.datetime.now()
    fim = agora + datetime.timedelta(days=7)
    return session.query(Evento).filter(Evento.agenda_id==agenda_id, Evento.start>=agora, Evento.start<=fim).all()

def lembrete_pendente(evento):
    agora = datetime.datetime.now()
    horas_ate_evento = (evento.start - agora).total_seconds() / 3600
    for lembrete in CADENCIA_LEMBRETES:
        chave = f"lembrete_enviado_{lembrete}"
        if getattr(evento, chave, False):
            continue
        if horas_ate_evento >= lembrete-1 and horas_ate_evento <= lembrete:
            return lembrete
    return None

def extrair_telefone(evento):
    # Extrai telefone do campo descrição
    import re
    match = re.search(r"(\+55)?\d{10,11}", evento.description or "")
    return match.group(0) if match else None

def buscar_ou_criar_contato_conversa(telefone):
    # Reutiliza lógica do worker buscar_criar_contato_conversa_worker
    session = get_db_session()
    contato = session.query(Contato).filter(Contato.telefone==telefone).first()
    if not contato:
        contato = Contato(telefone=telefone)
        session.add(contato)
        session.commit()
    conversa = session.query(Conversa).filter(Conversa.contato_id==contato.id).first()
    if not conversa:
        conversa = Conversa(contato_id=contato.id)
        session.add(conversa)
        session.commit()
    return contato, conversa

def gerar_mensagem_lembrete(evento, contato):
    from app.services.ai_service import gerar_resposta_agente
    profissional = evento.organizer
    data_hora = evento.start.strftime('%A, %d/%m às %H:%M')
    paciente = evento.summary
    descricao = evento.description
    status_pagamento = getattr(contato, 'asaas_status_cobranca', 'Cobrança ainda não foi gerada')
    prompt_usuario = f"Lembrete para consulta de {paciente} com {profissional} em {data_hora}. Detalhes: {descricao}. Status pagamento: {status_pagamento}."
    return gerar_resposta_agente('nutricionista', prompt_usuario)
    mensagem = f"Olá, {paciente}!\n\nPassando para lembrar da sua consulta {data_hora} com {profissional}.\nPor favor, confirme sua presença ou avise se precisar remarcar.\nStatus pagamento: {status_pagamento}"
    return mensagem

def enviar_mensagem_chatwoot(conversa_id, mensagem):
    url = f"{CHATWOOT_URL}/api/v1/accounts/{CHATWOOT_ACCOUNT_ID}/conversations/{conversa_id}/messages"
    payload = {"content": mensagem}
    headers = {"Content-Type": "application/json"}
    # TODO: Adicionar autenticação