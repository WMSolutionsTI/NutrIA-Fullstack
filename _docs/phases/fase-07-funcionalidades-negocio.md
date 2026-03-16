# Fase 07 — Funcionalidades de Negócio

> Funcionalidades core: agente IA secretária, anamnese inteligente pré-consulta, prontuário eletrônico, geração de plano alimentar por IA, envio de PDF, acompanhamento pós-consulta diário por IA, escalação humana, agendamentos, Asaas (pagamentos).

## Descrição

Esta fase implementa o diferencial competitivo do NutrIA-Pro: o ciclo completo de atendimento automatizado por IA — da anamnese até o acompanhamento diário pós-consulta.

## Feature 1: Agente de IA Secretária

O nutricionista configura no painel:
- **Nome** da secretária virtual (ex: "Ana")
- **Prompt de contexto** — especialidade, tom de voz, informações da clínica
- **Horário de atendimento** — quando o agente responde automaticamente
- **Mensagem fora do horário** — resposta automática fora do expediente
- **Mensagem de boas-vindas** — primeira mensagem para novos clientes
- **Tópicos para escalação** — assuntos que ativam atendimento humano automaticamente

## Feature 2: Anamnese Inteligente Pré-Consulta ⭐ DIFERENCIAL

Após o agendamento confirmado, o `AnamnesisWorker` inicia automaticamente:

```
Agendamento confirmado
        ↓
AnamnesisWorker ativado (via fila anamnesis.conductor)
        ↓
Envia perguntas sequenciais ao paciente via Chatwoot
(texto ou voz — paciente escolhe o canal preferido)
        ↓
Coleta: histórico médico, medicamentos, alergias,
        objetivos, restrições financeiras, preferências
        alimentares, hábitos, atividade física,
        histórico de peso, exames anteriores, etc.
        ↓
Respostas gravadas em AnamnesisSession + AnamnesisAnswer
(áudio transcrito automaticamente via Whisper/Retell)
        ↓
Anamnese completa → prontuário atualizado
        ↓
Notifica nutricionista: "Anamnese de [Paciente] concluída"
```

**Suporte a voz:**
- Paciente pode responder por áudio no WhatsApp
- `AnamnesisTranscriberWorker` transcreve automaticamente
- Áudio original + transcrição salvos no MinIO e no prontuário

## Feature 3: Prontuário Eletrônico Completo

A nutricionista visualiza e complementa durante a consulta:
- Dados da anamnese (pré-preenchidos pela IA)
- **Medidas antropométricas:** peso, altura, IMC, % gordura, circunferências
- **Exames solicitados e resultados**
- **Preferências alimentares e aversões**
- **Restrições financeiras** (faixa de gasto mensal com alimentação)
- **Hábitos e rotina** (horários, trabalho, sono)
- **Nível e tipo de atividade física**
- **Histórico de dietas anteriores**
- **Observações clínicas livres** (campo texto rico)
- **Tags clínicas** (ex: diabético, hipertenso, vegetariano)

## Feature 4: Geração de Plano Alimentar por IA ⭐ DIFERENCIAL

Após finalização da consulta:

```
Nutricionista marca consulta como "concluída"
        ↓
Evento consultation.completed → fila mealplan.generator
        ↓
MealPlanGeneratorWorker carrega prontuário completo
        ↓
LLM especialista em nutrição gera plano personalizado
(considera: objetivos, restrições, preferências,
 orçamento, atividade física, condições médicas)
        ↓
Plano salvo com status pending_approval
        ↓
Nutricionista recebe notificação no painel
        ↓
Nutricionista revisa, ajusta se necessário, aprova
        ↓
meal_plan.approved → fila mealplan.pdf.renderer
        ↓
MealPlanPdfWorker gera PDF profissional
(detalhado, visual, com todas as refeições,
 porções, substituições e orientações)
        ↓
PDF enviado via Chatwoot na conversa do paciente
```

## Feature 5: Acompanhamento Pós-Consulta Diário por IA ⭐ DIFERENCIAL

`FollowUpDailyWorker` (cron diário) para cada paciente com plano ativo:
- **Check-in diário:** "Como foi seu dia? Conseguiu seguir o plano?"
- **Lembretes de refeições** nos horários configurados no plano
- **Lembretes de atividade física** nos dias previstos
- **Dicas motivacionais** contextualizadas ao progresso do paciente
- **Monitoramento de aderência:** registra execução do plano em `FollowUpLog`
- **Escalação automática:** se paciente reportar problema grave → notifica nutricionista
- **Relatório semanal:** resumo de aderência enviado à nutricionista

## Feature 6: Fluxo de Escalação Humana

1. IA detecta necessidade → publica em `queue.human_escalation`
2. Worker desabilita `ai_agent_enabled` para o contato
3. Cliente recebe: *"Vou transferir você para [Nutricionista] agora. Aguarde!"*
4. Nutricionista recebe WhatsApp: *"⚠️ [Cliente] precisa de atendimento. [Link Chatwoot]"*
5. Nutricionista atende no Chatwoot
6. Nutricionista clica **"Retomar IA"** no painel
7. Cliente recebe: *"Estou de volta para continuar te ajudando! 😊"*
8. `ai_agent_enabled = true`, intervenção logada

## Outras Funcionalidades

- **Agendamentos** — CRUD completo, Google Calendar, lembretes automáticos
- **CRM** — perfil de cliente, notas clínicas, histórico de conversas
- **Campanhas** — segmentação, agendamento, estatísticas
- **Pagamentos** — integração Asaas, links de pagamento, PIX

## Referência

Ver `projects/fase-07-funcionalidades-negocio.yaml` para issues detalhadas.
