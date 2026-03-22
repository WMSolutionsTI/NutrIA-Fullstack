"""
Worker: Gestão de Ligações
Automatiza o registro, follow-up e cobrança de ligações telefônicas entre clínica e paciente.
- Processa eventos de chamada encerrada
- Extrai transcrição, telefone, nome, CPF, valor e vencimento
- Cria/atualiza contato e conversa
- Gera mensagem de follow-up via IA (prompt SOP)
- Envia follow-up e cobrança via Chatwoot
- Cria evento na agenda (Google/local)
- Cria/atualiza cobrança via Asaas
"""
import os
import requests
from app.domain.models.contato import Contato
from app.domain.models.conversa import Conversa
from app.domain.models.evento import Evento
from app.db.session import SessionLocal
from app.workers.quebrar_enviar_mensagens_worker import enviar_mensagens

CHATWOOT_URL = os.getenv("CHATWOOT_URL")
CHATWOOT_ACCOUNT_ID = os.getenv("CHATWOOT_ACCOUNT_ID")
CHATWOOT_INBOX_ID = os.getenv("CHATWOOT_INBOX_ID")
ASAAS_URL = os.getenv("ASAAS_URL", "https://api-sandbox.asaas.com")
COBRANCA_VALOR = float(os.getenv("COBRANCA_VALOR", "500"))

# --- Utilidades ---
def extrair_info_chamada(payload):
    return {
        "telefone": payload.get("headers", {}).get("x-retell-user-number", ""),
        "nome": payload.get("body", {}).get("nome", ""),
        "cpf": payload.get("body", {}).get("cpf", ""),
        "cobranca_vencimento": payload.get("body", {}).get("cobranca_vencimento", ""),
        "transcricao": payload.get("body", {}).get("call", {}).get("transcript", ""),
        "id_agenda": payload.get("body", {}).get("id_agenda", ""),
        "evento_inicio": payload.get("body", {}).get("evento_inicio", ""),
        "titulo": payload.get("body", {}).get("titulo", ""),
        "descricao": payload.get("body", {}).get("descricao", "")
    }

    session = SessionLocal()
    contato = session.query(Contato).filter(Contato.telefone==telefone).first()
    if not contato:
        contato = Contato(telefone=telefone, nome=nome, cpf=cpf)
        session.add(contato)
        session.commit()
    conversa = session.query(Conversa).filter(Conversa.contato_id==contato.id).first()
    if not conversa:
        conversa = Conversa(contato_id=contato.id)
        session.add(conversa)
        session.commit()
    return contato, conversa

    session = SessionLocal()
    evento = Evento(
        agenda_id=info["id_agenda"],
        start=info["evento_inicio"],
        summary=info["titulo"],
        description=info["descricao"] + f"\nTelefone: {info['telefone']}"
    )
    session.add(evento)
    session.commit()
    return evento

def criar_ou_buscar_cobranca(contato, valor, vencimento):
    # TODO: Integrar com Asaas API
    # Exemplo: criar cobrança e retornar link
    return {"resultado": "Cobrança criada.", "valor": valor, "vencimento": vencimento, "link": "https://asaas.com/pagamento/123"}

def gerar_mensagem_followup(transcricao):
    from app.services.ai_service import gerar_resposta_agente
    prompt_usuario = f"Resumo da ligação: {transcricao}"
    return gerar_resposta_agente('vendedor', prompt_usuario)

    enviar_mensagens(CHATWOOT_ACCOUNT_ID, conversa_id, [mensagem])

    mensagem = f"Olá {nome}, sua cobrança de R$ {valor:.2f} está disponível: {link}"
    enviar_mensagens(CHATWOOT_ACCOUNT_ID, conversa_id, [mensagem])