# Fase 14 — IA Nutricional (Anamnese, Plano Alimentar e Acompanhamento)

> Implementação completa do ciclo de IA nutricional: anamnese inteligente pré-consulta via Chatwoot (texto e voz), geração automatizada de plano alimentar, renderização de PDF profissional e agente de acompanhamento pós-consulta diário.

## Descrição

Esta fase implementa o maior diferencial competitivo do NutrIA-Pro: o ciclo completo de atendimento nutricionista automatizado por IA, do pré-consulta ao acompanhamento diário. É a feature que justifica a assinatura do SaaS.

## Fluxo Completo

```
1. Agendamento confirmado
         ↓
2. AnamnesisWorker inicia entrevista pré-consulta
   (perguntas via Chatwoot — texto ou voz)
         ↓
3. Respostas gravadas no prontuário (AnamnesisSession)
   Áudios transcritos pelo AnamnesisTranscriberWorker
         ↓
4. Nutricionista visualiza anamnese no painel antes da consulta
         ↓
5. Durante a consulta: nutricionista complementa prontuário
   (medidas, exames, preferências, restrições, hábitos, etc.)
         ↓
6. Consulta marcada como concluída
         ↓
7. MealPlanGeneratorWorker gera plano alimentar completo com LLM
         ↓
8. Nutricionista revisa, ajusta e aprova no painel
         ↓
9. MealPlanPdfWorker renderiza PDF profissional
         ↓
10. PDF enviado ao paciente via Chatwoot
         ↓
11. FollowUpDailyWorker inicia acompanhamento diário
    (dicas, lembretes, check-ins, motivação)
```

## Módulo 1: Anamnese Inteligente

### AnamnesisWorker
- Ativado por evento `appointment.confirmed`
- Prompt de anamnese configurável por tenant (nutricionista personaliza as perguntas)
- Envia perguntas em sequência lógica (não todas de uma vez — UX conversacional)
- Aguarda resposta, valida completude, avança para próxima pergunta
- Detecta respostas por voz (mensagem de áudio) e roteia para `AnamnesisTranscriberWorker`
- Finaliza quando todas as categorias estão cobertas
- Salva em `AnamnesisSession` com status `completed`
- Notifica nutricionista via painel e WhatsApp

### AnamnesisTranscriberWorker
- Consome fila `anamnesis.transcriber`
- Baixa arquivo de áudio do Chatwoot
- Envia para Whisper API (OpenAI) ou Retell para transcrição
- Persiste: `AnamnesisAnswer.text` (transcrição) + `AnamnesisAnswer.audio_url` (original no MinIO)
- Retorna controle ao `AnamnesisWorker` para continuar o fluxo

### Categorias de Anamnese Cobertas
| Categoria | Exemplos de Perguntas |
|-----------|----------------------|
| Objetivos | Perder peso? Ganhar massa? Controlar glicemia? |
| Histórico médico | Doenças, medicamentos, cirurgias |
| Alergias e intolerâncias | Lactose, glúten, frutos do mar |
| Preferências alimentares | Alimentos que gosta / não gosta |
| Restrições financeiras | Orçamento mensal para alimentação |
| Hábitos e rotina | Horários, trabalho, deslocamento |
| Atividade física | Tipo, frequência, intensidade |
| Histórico de dietas | Tentativas anteriores, resultados |
| Sono e estresse | Horas de sono, nível de estresse |

## Módulo 2: Geração de Plano Alimentar

### MealPlanGeneratorWorker
- Ativado por evento `consultation.completed`
- Carrega prontuário completo via `db_read` (anamnese + dados da consulta)
- Prompt estruturado para LLM especialista em nutrição:
  - Objetivo do paciente
  - Restrições (médicas, alimentares, financeiras)
  - Preferências e aversões
  - Nível de atividade física
  - Condições médicas relevantes
- LLM gera plano com: VET, macros, refeições detalhadas, substituições, orientações
- Salva `MealPlan` com status `pending_approval`
- Notifica nutricionista

### MealPlanPdfWorker
- Ativado por evento `meal_plan.approved`
- Template profissional de PDF com:
  - Cabeçalho com logo do nutricionista/clínica (personalizado por tenant)
  - Dados do paciente e objetivos
  - VET e distribuição de macronutrientes (com gráfico)
  - Cardápio detalhado por refeição (café, almoço, jantar, lanches)
  - Porções em medidas caseiras + gramas
  - Lista de substituições permitidas
  - Orientações gerais e dicas do nutricionista
  - Rodapé com informações de contato
- Upload para MinIO: `/{tenant_id}/meal-plans/{client_id}/{plan_id}.pdf`
- Envia PDF via Chatwoot com mensagem personalizada

## Módulo 3: Acompanhamento Pós-Consulta Diário

### FollowUpDailyWorker (cron diário)
- Executa diariamente para cada paciente com plano ativo
- Personaliza abordagem com base em:
  - Dia do plano (dia 1 vs. semana 3 = mensagens diferentes)
  - Histórico de aderência (paciente que está indo bem vs. com dificuldades)
  - Horário de refeições do plano
  - Atividade física prevista para o dia
- Interações:
  - **Check-in matinal:** "Bom dia [Nome]! Como você está hoje?"
  - **Lembretes de refeição:** nos horários do plano
  - **Lembrete de atividade:** nos dias de treino
  - **Check-in noturno:** "Como foi seu dia? Conseguiu seguir o plano?"
  - **Dica semanal:** conteúdo educativo sobre nutrição
- Registra tudo em `FollowUpLog`
- Escalação automática se paciente reportar sintomas preocupantes

## Modelos de Dados

```python
class AnamnesisSession(Base):
    id: UUID
    tenant_id: UUID
    client_id: UUID
    appointment_id: UUID
    status: Enum[in_progress, completed, skipped]
    started_at: datetime
    completed_at: datetime | None
    answers: List[AnamnesisAnswer]

class AnamnesisAnswer(Base):
    id: UUID
    session_id: UUID
    question_key: str        # ex: "financial_restriction"
    question_text: str
    answer_text: str         # texto ou transcrição do áudio
    answer_audio_url: str | None  # URL no MinIO se respondido por voz
    answered_at: datetime

class MealPlan(Base):
    id: UUID
    tenant_id: UUID
    client_id: UUID
    appointment_id: UUID
    status: Enum[generating, pending_approval, approved, sent]
    content_json: dict       # plano estruturado gerado pelo LLM
    pdf_url: str | None      # URL no MinIO após geração
    approved_by: UUID | None
    approved_at: datetime | None
    sent_at: datetime | None
    version: int

class FollowUpLog(Base):
    id: UUID
    tenant_id: UUID
    client_id: UUID
    meal_plan_id: UUID
    log_date: date
    message_type: Enum[checkin, meal_reminder, activity_reminder, tip, escalation]
    message_sent: str
    client_response: str | None
    adherence_score: int | None   # 0-100
```

## Configurações por Tenant

O nutricionista pode personalizar no painel:
- Perguntas de anamnese (adicionar/remover/reordenar)
- Tom de voz do agente de anamnese
- Template de PDF (logo, cores, informações de contato)
- Frequência e horários do follow-up
- Mensagens padrão do follow-up
- Critérios para escalação automática

## Referência

Nova fase — criar `projects/fase-14-ia-nutricional.yaml` com issues detalhadas.
