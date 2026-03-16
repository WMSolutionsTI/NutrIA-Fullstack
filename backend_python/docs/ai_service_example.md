# Exemplo de uso: Serviço de IA

## Chamada básica
```python
from app.services.ai_service import gerar_resposta_agente

resposta = gerar_resposta_agente(
    assunto="nutricionista",
    prompt_usuario="Quais alimentos são recomendados para hipertensão?",
    contexto="Paciente com restrição de sódio e histórico familiar de pressão alta."
)
print(resposta)
```

## Chamada para agente financeiro
```python
resposta = gerar_resposta_agente(
    assunto="agente_financeiro",
    prompt_usuario="Como posso renegociar o boleto vencido?",
    contexto="Cliente atrasou pagamento do plano mensal."
)
print(resposta)
```

## Chamada para consultor
```python
resposta = gerar_resposta_agente(
    assunto="consultor",
    prompt_usuario="Quais métricas SaaS devo acompanhar para escalar o negócio?"
)
print(resposta)
```

## Chamada para incentivador
```python
resposta = gerar_resposta_agente(
    assunto="incentivador",
    prompt_usuario="Preciso motivar o paciente a seguir o plano alimentar."
)
print(resposta)
```
