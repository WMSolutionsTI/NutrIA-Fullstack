# AI Agent Architecture — NutrIA-Pro

## Core Purpose

The central purpose of NutrIA-Pro is that **nutritionists should never need to manually respond to clients**. All client communication is handled by an **AI agent (secretária virtual)** that uses the nutritionist's own context/prompt configured in the professional's panel. The nutritionist only intervenes when explicitly requested or when the AI escalates.

Beyond communication, the AI handles the **complete consultation cycle**:
1. Pre-consultation anamnesis interview (text or voice)
2. Meal plan generation post-consultation
3. Daily post-consultation follow-up and adherence monitoring

---

## AI Agents Overview

| Agent | Trigger | Channel | Purpose |
|-------|---------|---------|---------|
| **Secretária Virtual** | Incoming message | Chatwoot/WhatsApp | Answer, schedule, escalate |
| **Agente de Anamnese** | Appointment confirmed | Chatwoot/WhatsApp | Pre-consultation interview |
| **Agente Gerador de Plano** | Consultation completed | Internal (LLM) | Generate meal plan |
| **Agente de Acompanhamento** | Daily cron (post-plan) | Chatwoot/WhatsApp | Daily follow-up |

---

## Nutritionist Configuration Panel

Each nutritionist configures their AI persona in their dashboard:

- **Nome da secretária** — e.g. "Ana"
- **Prompt de contexto** — specialty, tone of voice, clinic information
- **Horário de atendimento** — operating hours for the agent
- **Mensagem fora do horário** — out-of-hours auto-reply
- **Mensagem de boas-vindas** — first-contact greeting
- **Tópicos para escalação** — topics that automatically trigger human escalation
- **Perguntas de anamnese** — customizable anamnesis questionnaire
- **Template de PDF** — logo, colors, contact info for meal plan PDF
- **Configurações de follow-up** — frequency, hours, escalation criteria

---

## Message Flow

```
Client (WhatsApp) → Evolution API → Chatwoot → Webhook → Backend
  → Verify ai_agent_enabled flag for contact
    → [enabled]  → Publish to queue.message_processor → Worker → n8n (Secretária v3) → LLM → Response via Chatwoot/WhatsApp
    → [disabled] → Message held in Chatwoot for human attendant
```

---

## Anamnesis Flow (Pre-Consultation)

```
appointment.confirmed event
        ↓
AnamnesisWorker (queue: anamnesis.conductor)
        ↓
Sequential questions via Chatwoot
  → Text response: save to AnamnesisAnswer
  → Voice response: route to AnamnesisTranscriberWorker
        ↓
AnamnesisTranscriberWorker (queue: anamnesis.transcriber)
  → Download audio → Whisper/Retell STT → Save transcription
        ↓
All categories covered → AnamnesisSession.status = completed
        ↓
Notify nutritionist: "Anamnese de [Patient] concluída"
```

---

## Consultation & Meal Plan Flow

```
consultation.completed event
        ↓
MealPlanGeneratorWorker (queue: mealplan.generator)
  → Load full medical record (via db_read)
  → Call LLM with full context
  → Save MealPlan (status: pending_approval)
        ↓
Nutritionist reviews & approves in panel
        ↓
meal_plan.approved event
        ↓
MealPlanPdfWorker (queue: mealplan.pdf.renderer)
  → Render professional PDF
  → Upload to MinIO
  → Send via Chatwoot to patient
```

---

## Daily Follow-Up Flow

```
FollowUpDailyWorker (cron: daily)
  → For each patient with active meal plan:
    → Send morning check-in
    → Send meal reminders (at plan times)
    → Send activity reminders (on exercise days)
    → Send evening check-in
    → Log in FollowUpLog
    → Escalate if concerning response detected
```

---

## Human Escalation Flow

1. AI detects need for escalation (complex query, client requests human, or configured topic matched)
2. Publish event to `queue.human_escalation`
3. **HumanEscalationWorker**:
   - Sets `ai_agent_enabled = false` for the contact
   - Sends client message: *"Vou transferir você para [Nome do Nutricionista] agora. Aguarde!"*
   - Sends WhatsApp to nutritionist: *"⚠️ Atenção! [Nome do Cliente] precisa de atendimento humano. Acesse: [link Chatwoot]"*
   - Notifies nutritionist panel
4. Nutritionist attends via Chatwoot
5. Nutritionist clicks **"Retomar IA"** in the panel (or calls `PATCH /api/v1/conversations/{id}/ai-agent`)
6. **AIResumeWorker**:
   - Sets `ai_agent_enabled = true`
   - Sends client message: *"Olá! Estou de volta para continuar te ajudando! 😊"*
   - Logs the human intervention with timestamps

---

## Workflow Map: n8n vs. Backend Workers

| Workflow | Decision | Reason |
|----------|----------|--------|
| 01. Secretária v3 | **n8n** | Event-driven, visual LLM flow, complex branching |
| 02. Google Drive | **n8n** | External API, low volume, webhook-based |
| 03. Google Calendar Slots | **n8n** | External API, tenant OAuth per request |
| 04. Criar Evento Calendar | **n8n** | External API, low volume |
| 04.1 Atualizar Agendamento | **n8n** | External API, low volume |
| 05. Escalar Humano | **n8n + Worker** | n8n orchestrates, Worker handles state + DB |
| 06. Integração Asaas | **n8n** | Webhook-based, external payment integration |
| 07. Quebrar Mensagens | **Worker** | Queue-based, rate limiting, high volume |
| 08. Agente Assistente Interno | **n8n** | LLM calls, low volume, admin panel |
| 09. Desmarcar Agendamento | **n8n** | External API + notification, event-driven |
| 10. Buscar/Criar Contato | **n8n** | Chatwoot API calls, sub-workflow |
| 11. Lembretes Agendamento | **Worker** | Cron-based, DB-heavy, retry logic, high volume |
| 12. Gestão de Ligações | **n8n** | Retell AI webhooks, low volume |
| 13. Recuperação de Leads | **Worker** | Cron-based, DB-heavy, bulk processing |
| 14. Anamnese IA | **Worker** | Stateful session, high volume, sophisticated retry |
| 15. Transcrição de Voz | **Worker** | STT pipeline, binary file handling, high volume |
| 16. Geração Plano Alimentar | **Worker** | High-context LLM, DB-heavy, retry critical |
| 17. Render PDF Plano | **Worker** | Sequential pipeline: render → upload → send |
| 18. Acompanhamento Pós-Consulta | **Worker** | Daily cron, bulk, DB-heavy, personalized |
| Retell - Secretária v3 | **n8n** | Voice AI webhooks, Retell integration |

### Decision Criteria

**Stay in n8n when:**
- Triggered by webhooks or external events
- Requires visual flow for complex LLM branching
- Low-to-medium volume, external API integrations
- Needs easy modification by non-developers

**Convert to Worker when:**
- Cron-based scheduled execution at high volume
- Requires sophisticated retry logic and dead-letter handling
- Heavy database operations (bulk reads/writes)
- Rate limiting and queue backpressure management needed
- Stateful session management (e.g., multi-step anamnesis)
- Binary file processing (audio transcription, PDF rendering)

---

## Key Flags & State

| Field | Location | Description |
|-------|----------|-------------|
| `ai_agent_enabled` | `contacts` table (per tenant) | Controls whether AI processes messages for this contact |
| `ai_agent_prompt` | `tenants` table | The nutritionist's custom prompt/context |
| `ai_agent_name` | `tenants` table | Name of the virtual secretary |
| `ai_agent_hours` | `tenants` table | Operating hours (JSON) |
| `anamnesis_questions` | `tenants` table | Custom anamnesis questionnaire (JSON) |
| `meal_plan_template` | `tenants` table | PDF template config (logo, colors, contact info) |
| `followup_config` | `tenants` table | Follow-up schedule and escalation criteria (JSON) |

---

## Related Documents

- [`docs/phases/fase-14-ia-nutricional.md`](phases/fase-14-ia-nutricional.md) — Full AI nutritional cycle
- [`docs/phases/fase-15-banco-dados-ha.md`](phases/fase-15-banco-dados-ha.md) — Database HA & anti-lock strategy
- [`workflows/01-secretaria-v3.md`](workflows/01-secretaria-v3.md) — Main AI secretary
- [`workflows/05-escalar-humano.md`](workflows/05-escalar-humano.md) — Human escalation flow
- [`workflows/decision-matrix.md`](workflows/decision-matrix.md) — Full n8n vs. worker decision matrix
