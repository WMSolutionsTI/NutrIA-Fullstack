# ADR-005: n8n como engine de automação no-code

**Data:** 2026-03-09
**Status:** Aceito

---

## Contexto

O NutrIA-Pro possui fluxos de automação complexos (secretária IA, agendamentos, cobranças, lembretes) que precisam ser flexíveis e modificáveis sem deploy de código. Uma engine de automação visual reduz o tempo de ajuste de fluxos.

## Decisão

Usar **n8n** (self-hosted) como engine de automação, complementando os workers Python para fluxos de baixo volume e alta complexidade.

## Alternativas Consideradas

| Alternativa | Por que descartada |
|---|---|
| Make (Integromat) | SaaS; custo por operação; vendor lock-in; dados saem do servidor |
| Zapier | Idem Make; muito caro em escala |
| Apache Airflow | Focado em data pipelines; complexidade desnecessária para automações de negócio |
| Tudo em workers Python | Sem interface visual; dificulta ajustes rápidos de fluxo pelo operador |

## Divisão de Responsabilidades

| Responsabilidade | n8n | Workers Python |
|---|---|---|
| Fluxos visuais complexos | ✅ | |
| Alto volume (>1000/min) | | ✅ |
| Integrações externas pontuais | ✅ | |
| Processamento de mensagens | | ✅ |
| Lógica de negócio crítica | | ✅ |

## Consequências

### Positivas
- Fluxos modificáveis via UI sem deploy
- Mais de 400 integrações nativas
- Self-hosted: dados seguros, sem custo por execução
- Webhooks nativos para receber eventos externos

### Negativas / Trade-offs
- Não substitui workers Python para alto volume
- Versões self-hosted têm limitações vs. cloud
- Requer backup dos workflows exportados

## Referências

- https://docs.n8n.io/
- https://github.com/n8n-io/n8n
