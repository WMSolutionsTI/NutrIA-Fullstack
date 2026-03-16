# Fase 08 — Frontend

> Frontend em Next.js: dashboard do nutricionista, configuração do agente de IA, prontuário eletrônico completo, visualização e edição do plano alimentar gerado por IA, acompanhamento pós-consulta, relatórios.

## Descrição

Esta fase constrói o painel do nutricionista — a interface web onde o profissional configura o agente de IA, acompanha conversas, visualiza prontuários, revisa e aprova planos alimentares, e monitora o acompanhamento pós-consulta dos pacientes.

## Stack Frontend

- **Framework:** Next.js 14+ (App Router)
- **Linguagem:** TypeScript
- **Estilos:** Tailwind CSS + shadcn/ui
- **Estado:** Zustand + React Query
- **Autenticação:** NextAuth.js
- **Editor Rico:** TipTap (para prontuário e plano alimentar)
- **PDF Preview:** react-pdf (visualizar plano antes de enviar)

## Telas Principais

| Tela | Funcionalidade |
|------|---------------|
| Dashboard | Métricas do dia: consultas, anamneses pendentes, planos para aprovar |
| Configuração da IA | Nome, prompt, horários, mensagens, tópicos de escalação |
| Conversas | Visualização de conversas do Chatwoot + toggle AI agent |
| Agenda | Calendário de consultas, criação/edição de agendamentos |
| Prontuário do Paciente | Anamnese pré-preenchida pela IA + campos da consulta |
| Plano Alimentar | Editor do plano gerado pela IA, preview PDF, botão de aprovação |
| Acompanhamento | Timeline diária de follow-up, aderência ao plano, logs |
| Clientes | Lista, perfil, histórico de consultas e planos |
| Campanhas | Criação, segmentação, agendamento, stats |
| Assinatura | Plano atual, histórico de faturas, upgrade |

## Telas de Destaque

### Prontuário do Paciente
- Painel com todas as respostas da anamnese (separadas por categoria)
- Player de áudio inline para respostas gravadas por voz
- Seção editável pela nutricionista durante a consulta
- Histórico de todas as consultas anteriores

### Editor de Plano Alimentar
- Exibe plano gerado pela IA em formato editável
- Editor rico por refeição (café, almoço, jantar, lanches)
- Botão **"Regenerar com IA"** para ajustes pontuais
- Preview do PDF antes de aprovar
- Botão **"Aprovar e Enviar"** que dispara o envio ao paciente
- Histórico de versões do plano

### Dashboard de Acompanhamento
- Timeline visual do check-in diário de cada paciente
- Gráfico de aderência ao plano (% dos dias cumpridos)
- Alertas de pacientes sem interação > X dias
- Log completo de mensagens do agente de follow-up

## Feature Central: Painel de Configuração do Agente de IA

- Editor de prompt com preview em tempo real
- Configuração de horários de atendimento (por dia da semana)
- Lista de tópicos que escalam para humano automaticamente
- Botão **"Retomar IA"** visível nas conversas com `ai_agent_enabled = false`
- Histórico de intervenções humanas

## Referência

Ver `projects/fase-08-frontend.yaml` para issues detalhadas.
