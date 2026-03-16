"""
Worker: Agente de Recuperação de Leads
Automatiza o follow-up para leads que não responderam, com múltiplas tentativas e integração multicanal.
- Busca leads aguardando follow-up
- Verifica número de follow-ups e tempo desde última mensagem
- Gera mensagem personalizada via IA (prompt SOP)
- Envia mensagem via Chatwoot
- Atualiza status e contagem de follow-up
- Integra com ligações (telefone/WhatsApp) via webhooks
"""
import os
import datetime
import requests
from app.workers.quebrar_enviar_mensagens_worker import enviar_mensagens
from app.domain.models.cliente import Cliente
from app.domain.models.conversa import Conversa
from app.domain.models.lead import Lead
from app.db.session import SessionLocal


CHATWOOT_URL = os.getenv("CHATWOOT_URL")
CHATWOOT_ACCOUNT_ID = os.getenv("CHATWOOT_ACCOUNT_ID")
CHATWOOT_INBOX_ID = os.getenv("CHATWOOT_INBOX_ID")
MAX_FOLLOWUPS = int(os.getenv("MAX_FOLLOWUPS", "3"))
FOLLOW_UPS_HORAS = [6, 24, 48]
TIPO_FOLLOW_UPS = ['mensagem', 'ligacao', 'ligacao_whatsapp']
URL_WEBHOOK_LIGACOES = os.getenv("URL_WEBHOOK_LIGACOES")
URL_WEBHOOK_LIGACOES_WHATSAPP = os.getenv("URL_WEBHOOK_LIGACOES_WHATSAPP")
TELEFONE = os.getenv("TELEFONE")
TELEFONE_WHATSAPP = os.getenv("TELEFONE_WHATSAPP")

# --- Utilidades ---
def buscar_leads_aguardando_followup():
    session = get_db_session()
    agora = datetime.datetime.now()
    return session.query(Lead).filter(Lead.aguardando_followup==True).all()

def followup_excedido(lead):
    return lead.numero_followup >= MAX_FOLLOWUPS

def tempo_desde_ultima_mensagem(conversa):
    agora = datetime.datetime.now()
    if not conversa.last_non_activity_message:
        return None
    return (agora - conversa.last_non_activity_message.created_at).total_seconds() / 3600

def gerar_mensagem_recuperacao(lead):
    from app.services.ai_service import gerar_resposta_agente
    prompt_usuario = f"Lead: {lead.nome}, número de follow-up: {lead.numero_followup}, contexto: {lead.contexto}"
    return gerar_resposta_agente('incentivador', prompt_usuario)

    # Usa worker de envio de mensagens
    enviar_mensagens(CHATWOOT_ACCOUNT_ID, conversa_id, [mensagem])

    session = SessionLocal()
    lead.aguardando_followup = False
    lead.numero_followup += 1
    session.add(lead)
    session.commit()

    leads = buscar_leads_aguardando_followup()
    for lead in leads:
        if followup_excedido(lead):
            lead.aguardando_followup = False
            session = SessionLocal()
            session.add(lead)
            session.commit()
            continue
        conversa = lead.conversa
        horas = tempo_desde_ultima_mensagem(conversa)
        if horas is None or horas < FOLLOW_UPS_HORAS[lead.numero_followup]:
            continue
        mensagem = gerar_mensagem_recuperacao(lead)
        enviar_mensagem_chatwoot(conversa.id, mensagem)
        atualizar_status_followup(lead)
        # TODO: Integrar com ligações (telefone/WhatsApp) via webhooks