import pytest
from app.services.ai_service import gerar_resposta_agente

def test_nutricionista():
    resposta = gerar_resposta_agente(
        assunto="nutricionista",
        prompt_usuario="Quais alimentos são recomendados para hipertensão?",
        contexto="Paciente com restrição de sódio."
    )
    assert isinstance(resposta, str)
    assert len(resposta) > 0

def test_agente_financeiro():
    resposta = gerar_resposta_agente(
        assunto="agente_financeiro",
        prompt_usuario="Como renegociar boleto vencido?",
        contexto="Cliente atrasou pagamento."
    )
    assert isinstance(resposta, str)
    assert len(resposta) > 0

def test_incentivador():
    resposta = gerar_resposta_agente(
        assunto="incentivador",
        prompt_usuario="Motivar paciente a seguir plano alimentar."
    )
    assert isinstance(resposta, str)
    assert len(resposta) > 0
