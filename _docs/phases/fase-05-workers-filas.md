# Fase 05 — Workers e Filas (RabbitMQ)

> Sistema de workers e arquitetura de filas com RabbitMQ: processamento assíncrono de mensagens, retry logic, dead letter queues, workers para: anamnese IA, geração de plano alimentar, acompanhamento pós-consulta, envio de PDF, cobranças, lembretes.

## Descrição

Esta fase constrói o motor assíncrono do NutrIA-Pro — o sistema de workers RabbitMQ que processa todos os eventos em background com resiliência, retry e escalonamento horizontal. Inclui os novos workers do ciclo completo de consulta com IA.

## Arquitetura de Filas

| Exchange | Tipo | Filas |
|----------|------|-------|
| `chatwoot.events` | topic | `message.processor`, `conversation.processor` |
| `automation.triggers` | topic | `automation.executor` |
| `notifications.outbound` | direct | `notification.sender` |
| `scheduler.tasks` | topic | `scheduler.executor` |
| `billing.events` | direct | `billing.processor` |
| `anamnesis.events` | topic | `anamnesis.conductor`, `anamnesis.transcriber` |
| `consultation.events` | topic | `mealplan.generator`, `mealplan.pdf.renderer` |
| `followup.events` | topic | `followup.daily.agent` |
| `deadletter` | direct | `deadletter.queue` |

## Workers Principais

### Workers Existentes
- **MessageProcessorConsumer** — processa mensagens inbound, upsert de cliente, grava no DB
- **NotificationSenderConsumer** — envia mensagens outbound via Chatwoot
- **SchedulerWorker** — polling de tarefas agendadas e publicação nas filas
- **HumanEscalationWorker** — gerencia escalação humana e desabilita flag AI
- **AIResumeWorker** — reativa agente de IA e envia mensagem de retomada
- **DLQ Handler** — monitora e registra mensagens com falha

### Novos Workers — Ciclo de Consulta com IA

- **AnamnesisWorker** — conduz entrevista pré-consulta via Chatwoot após agendamento confirmado
  - Envia perguntas sequenciais ao paciente (texto ou voz via Retell/Whisper)
  - Aguarda resposta, valida, persiste no `AnamnesisSession`
  - Detecta quando a anamnese está completa e notifica a nutricionista
  - Suporta respostas por áudio: transcreve via STT e salva texto + áudio no MinIO

- **AnamnesisTranscriberWorker** — processa mensagens de voz recebidas durante a anamnese
  - Consome `anamnesis.transcriber`
  - Baixa o áudio do Chatwoot/MinIO
  - Envia para STT (Whisper/Retell)
  - Persiste transcrição e retorna para o `AnamnesisWorker` continuar o fluxo

- **MealPlanGeneratorWorker** — geração do plano alimentar após finalização da consulta
  - Acionado por evento `consultation.completed`
  - Carrega o prontuário completo do paciente (via `db_read`)
  - Chama LLM especialista em nutrição com todo o contexto
  - Salva plano em `MealPlan` com status `pending_approval`
  - Notifica nutricionista para revisão no painel

- **MealPlanPdfWorker** — renderiza e envia o plano alimentar em PDF
  - Acionado após `meal_plan.approved`
  - Gera PDF profissional e detalhado com WeasyPrint/ReportLab
  - Faz upload para MinIO sob `/{tenant_id}/meal-plans/{plan_id}.pdf`
  - Envia PDF via Chatwoot na conversa do paciente

- **FollowUpDailyWorker** — agente de IA de acompanhamento pós-consulta (cron diário)
  - Processa pacientes com plano ativo e data de início passada
  - Verifica aderência ao plano (check-in diário)
  - Envia dicas motivacionais, lembretes de refeições e atividades físicas
  - Registra cada interação em `FollowUpLog`
  - Escala para nutricionista se detectar problema grave

## Padrões de Resiliência

- **Retry:** 3 tentativas com backoff 2s/4s/8s via headers de mensagem
- **Idempotência:** Redis key `worker:processed:{message_id}` (TTL 48h)
- **DLQ:** mensagens após 3 falhas → `deadletter.queue` + alerta
- **Graceful Shutdown:** SIGTERM → finalizar mensagem em andamento → fechar conexão
- **Backpressure:** prefetch_count por worker configurável (evita sobrecarga de memória)
- **Circuit Breaker:** Redis key para rastrear falhas consecutivas de LLM/STT

## Referência

Ver `projects/fase-05-workers-filas.yaml` para issues detalhadas.
