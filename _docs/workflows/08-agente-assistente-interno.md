# 08. Agente Assistente Interno

> **Type:** n8n Flow
> **Trigger:** webhook (requests from nutritionist's dashboard panel)
> **Status:** active

## Short Description

An internal AI assistant for the nutritionist's panel that answers queries about their clients, appointments, and business metrics by combining LLM reasoning with NutrIA-Pro data access.

## Responsibilities

- Receive natural language queries from the nutritionist's dashboard
- Fetch relevant context from NutrIA-Pro backend (client data, appointments, metrics)
- Send query + context to LLM for intelligent response generation
- Return structured answers to the frontend dashboard
- Support tool calls: client lookup, appointment stats, message history

## Integration Points

- **NutrIA-Pro Backend API** — client data, appointments, analytics
- **LLM (OpenAI/Anthropic)** — query answering with function calling
- **Frontend Dashboard** — webhook trigger, response consumer

## Implementation Decision

**Stay in n8n.** LLM integration with complex tool-calling branching, admin panel queries, low volume. Visual flow is valuable for extending the assistant's capabilities.
