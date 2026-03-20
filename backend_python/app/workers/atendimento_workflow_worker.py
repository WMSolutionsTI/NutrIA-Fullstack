from app.workers.quebrar_enviar_mensagens_worker import enviar_mensagens


def process_atendimento_workflow(payload):
    """Processa workflows de atendimento com base no tipo de cliente."""
    account_id = payload.get("account_id")
    conversation_id = payload.get("conversation_id")
    message = payload.get("message")
    workflow = payload.get("workflow")

    if workflow == "potencial":
        resposta = (
            "Olá! Sou a assistente virtual da sua nutricionista. "
            "Vou te ajudar com informações sobre planos, horários e especialidades. "
            "Qual a sua principal dúvida hoje?"
        )
    elif workflow == "ativo":
        resposta = (
            "Perfeito, vou continuar seu acompanhamento. "
            "Informe seus sintomas/níveis de progresso e vamos ajustar o plano nutricional."
        )
    elif workflow == "recuperacao":
        resposta = (
            "Estamos sentindo sua falta! Temos uma oferta especial para retomar seu acompanhamento. "
            "Quer conversar sobre o plano que estava usando?"
        )
    elif workflow == "manter_relacionamento":
        resposta = (
            "Parabéns pelos resultados! "
            "Temos novidades exclusivas e pesquisa de satisfação. Posso te enviar?"
        )
    else:
        resposta = "Recebido. Estamos processando sua solicitação e em breve te responderemos."

    if account_id and conversation_id:
        enviar_mensagens(account_id, conversation_id, [resposta])

    # Retornar objeto para testes se necessário
    return {
        "status": "ok",
        "workflow": workflow,
        "message": resposta
    }
