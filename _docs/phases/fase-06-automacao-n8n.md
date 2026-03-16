# Fase 06 — Engine de Automação (n8n)

> Workflows n8n: secretária virtual IA, escalação humana, Google Calendar, Asaas, lembretes, voz (Retell). Critério claro de n8n vs. Worker para cada fluxo.

## Descrição

Esta fase configura o n8n como engine de automação para fluxos event-driven e de baixo volume. Fluxos de alto volume, cron-based ou com lógica de retry complexa são implementados como Workers nativos.

## Critério de Decisão: n8n vs. Worker

| Critério | n8n | Worker |
|----------|-----|--------|
| Volume | Baixo a médio | Alto |
| Trigger | Webhook / evento externo | Fila / cron |
| LLM | Sim (branching visual) | Sim (alta escala) |
| Retry | Simples | Sofisticado (DLQ) |
| DB | Leve | Pesado (bulk) |
| Modificação | Fácil (non-dev) | Requer deploy |

## Mapa de Workflows

| Workflow | Decisão | Motivo |
|----------|---------|--------|
| 01. Secretária v3 | **n8n** | Event-driven, LLM visual, branching complexo |
| 02. Google Drive | **n8n** | API externa, baixo volume, webhook |
| 03. Google Calendar Slots | **n8n** | API externa, OAuth por tenant |
| 04. Criar Evento Calendar | **n8n** | API externa, baixo volume |
| 04.1 Atualizar Agendamento | **n8n** | API externa, baixo volume |
| 05. Escalar Humano | **n8n + Worker** | n8n orquestra, Worker gerencia estado + DB |
| 06. Integração Asaas | **n8n** | Webhook, integração de pagamento externa |
| 07. Quebrar Mensagens | **Worker** | Fila, rate limiting, alto volume |
| 08. Agente Assistente Interno | **n8n** | LLM, baixo volume, painel admin |
| 09. Desmarcar Agendamento | **n8n** | API externa + notificação |
| 10. Buscar/Criar Contato | **n8n** | Sub-workflow Chatwoot API |
| 11. Lembretes Agendamento | **Worker** | Cron, DB-heavy, retry, alto volume |
| 12. Gestão de Ligações | **n8n** | Webhooks Retell AI, baixo volume |
| 13. Recuperação de Leads | **Worker** | Cron, DB-heavy, bulk processing |
| 14. Anamnese IA | **Worker** | Sessão stateful, alto volume, retry sofisticado |
| 15. Geração Plano Alimentar | **Worker** | LLM de alto contexto, retry, DB-heavy |
| 16. PDF Plano Alimentar | **Worker** | Render + upload + envio, pipeline sequencial |
| 17. Acompanhamento Pós-Consulta | **Worker** | Cron diário, bulk, DB-heavy |
| Retell - Secretária v3 | **n8n** | Webhooks de voz, integração Retell |

## Workflows Prioritários

### 01. Secretária Virtual v3
- Recebe mensagem → consulta prompt do tenant → chama LLM → responde via Chatwoot
- Detecta intenção de agendamento → aciona fluxo de agenda
- Detecta necessidade de escalação → publica em `queue.human_escalation`

### 05. Escalação Humana
- n8n detecta trigger → publica evento no Worker
- Worker: desativa IA, notifica nutricionista, loga intervenção

## Referência

Ver `projects/fase-06-automacao-n8n.yaml` para issues detalhadas.
