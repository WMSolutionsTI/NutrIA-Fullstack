# Relatório de Auditoria Completa (Backend, Workers, Deploy e Segurança)
Data: 21/03/2026  
Projeto: NutrIA-Fullstack

## 1) Escopo desta auditoria
- Revisão de operabilidade dos workers e filas.
- Verificação de aderência funcional ao fluxo de suporte da nutricionista.
- Diagnóstico de prontidão para deploy em VPS Contabo com Docker (rede overlay), Cloudflared em container, e frontend na Vercel.
- Levantamento de riscos técnicos, de segurança, observabilidade e escalabilidade.
- Geração de plano de tarefas para deixar o sistema pronto para produção.

## 2) Ações executadas nesta rodada
- Classificação de workers por operabilidade (importabilidade real, dependências, aderência ao domínio atual).
- Arquivamento de workers não operantes em `backend_python/app/workers/_arquivo`.
- Validação de import dos workers ativos (`FAIL COUNT 0` após arquivamento).
- Revisão dos artefatos de deploy (`_infra/docker-compose.yml`, `_infra/docker-compose.prod.yml`, `docker-stack.yml`).
- Revisão de testes backend e estado da suíte.

## 3) Workers: status atual
### 3.1 Workers ativos (operantes no contexto atual)
- `admin_monitor_worker.py`
- `asaas_worker.py` (operante tecnicamente, mas integração precisa hardening)
- `assistente_interno_worker.py`
- `atendimento_workflow_worker.py`
- `atualizar_agendamento_worker.py` (placeholder estável)
- `baixar_enviar_arquivo_worker.py` (parcial: upload Chatwoot mock)
- `cadastro_assinatura_worker.py` (parcial: e-mail/Chatwoot stubs)
- `chatwoot_attachment_worker.py`
- `chatwoot_message_worker.py`
- `escalar_humano_worker.py`
- `minio_worker.py`
- `monitor_app_worker.py` (parcial: métricas mock)
- `quebrar_enviar_mensagens_worker.py`
- `rabbitmq_worker.py`
- `redis_worker.py`
- `retell_secretaria_v3_worker.py` (placeholder estável)
- `suporte_nutri_worker.py`

### 3.2 Workers não operantes movidos para arquivo
Movidos para `backend_python/app/workers/_arquivo`:
- `agente_lembretes_agendamento_worker.py`
- `buscar_criar_contato_conversa_worker.py`
- `configuracoes_worker.py`
- `criar_evento_google_worker.py`
- `desmarcar_agendamento_worker.py`
- `gestao_ligacoes_worker.py`
- `google_calendar_worker.py`
- `plano_pdf_worker.py`
- `recuperacao_leads_worker.py`
- `secretaria_v3_worker.py`

Motivos principais:
- Dependências ausentes/incompatíveis com o código atual (`backend.shared`, `app.domain.models.lead`, `contato`, `evento`, `app.db.session`, libs não instaladas).
- Trechos legados/stub sem fluxo executável completo.
- Desalinhamento com o modelo atual (Chatwoot + SQLAlchemy + APIs existentes).

## 4) Estado funcional do sistema (visão de negócio)
### 4.1 Fluxos já funcionais/recentes
- Webhook Chatwoot com criação de cliente potencial e persistência de conversa.
- Escalonamento para atendimento direto da nutri e retorno ao modo IA.
- Validação de contato tipo nutri por código.
- Progressão de status com regras básicas (`potencial`, `ativo`, `inativo`, `satisfeito`).
- Gestão de caixa de entrada no backend (resumo, pendências, limites).
- Isolamento de tenant reforçado em rotas de conversa.

### 4.2 Lacunas para cumprir a proposta “suporte total”
- Ausência de workflows robustos de agendamento/cobrança/pós-atendimento ponta a ponta (integrações reais ainda parciais).
- Ausência de orquestração confiável para todos os tópicos de fila definidos.
- Persistência de contexto de atendimento ainda sem governança completa (versionamento de contexto, replay, auditoria forte).
- Parte dos serviços de “secretária 24h” ainda depende de placeholders.

## 5) Diagnóstico de deploy (Contabo + Docker overlay + Cloudflared + Vercel)
## 5.1 Bloqueios críticos (P0)
- `_infra/docker-compose.yml` e `_infra/docker-compose.prod.yml` estão estruturalmente inconsistentes (blocos concatenados e trechos inválidos).
- Compose e stack ainda referenciam workers arquivados (não operantes), o que causará falha de start.
- Topologia de containers precisa ser consolidada em um único manifesto de produção válido.
- Estratégia de filas não está totalmente alinhada entre produtor e consumidores por tipo de workload.

### 5.2 Riscos de segurança (P0/P1)
- Necessário validar assinatura/autenticidade do webhook Chatwoot.
- Secrets e credenciais precisam sair de arquivos e ir para secret store (Docker secrets/Cloudflare/CI).
- Rate limit/abuso por tenant ainda precisa hardening em rotas sensíveis.
- Revisar políticas CORS e cabeçalhos de segurança para produção.
- Definir política de retenção e criptografia para dados e arquivos (LGPD).

### 5.3 Observabilidade/operação (P1)
- Faltam métricas reais para workers, filas, latência de webhook, erro por integração.
- Falta tracing e correlação por `tenant_id`, `cliente_id`, `conversation_id`.
- Falta healthchecks de fila e readiness por worker.

## 6) Testes e qualidade
- Testes críticos do backend (auth/chatwoot/conversa isolamento) estão operando sem bloqueio de TestClient na base atual.
- Suite completa ainda exige ajuste em cenários legados para eliminar travamentos e cobrir integrações reais.
- É obrigatório estabelecer pipeline CI com:
- lint + type check
- testes unitários + integração
- smoke test de deploy
- validação do compose de produção

## 7) Plano de tarefas para “pronto para produção”
### Fase P0 (obrigatória antes do deploy)
1. Criar `docker-compose.prod.v2.yml` limpo e válido, removendo serviços quebrados e referências a workers arquivados.
2. Definir matriz final de workers por responsabilidade:
- `worker-rabbitmq-consumer-atendimento`
- `worker-chatwoot-outbound`
- `worker-onboarding-assinatura`
- `worker-monitoramento`
3. Implementar DLQ/retry/backoff/idempotência por fila no RabbitMQ.
4. Validar webhook Chatwoot com assinatura e controle anti-replay.
5. Consolidar secrets (JWT, DB, Rabbit, Redis, MinIO, Chatwoot, Asaas, OpenAI) fora do repositório.
6. Corrigir endpoint admin metrics (typo de função) e revisar endpoints sem proteção.
7. Publicar runbook de incidentes (fila parada, webhook indisponível, atraso de processamento).

### Fase P1 (estabilidade e escala)
1. Implementar integrações reais pendentes (Google Agenda, Asaas, arquivos com upload real no fluxo de atendimento).
2. Telemetria: Prometheus/Grafana + logs estruturados centralizados.
3. Índices e otimizações de banco por consultas de conversa/cliente/tenant.
4. Testes de carga em webhook e consumidores de fila.
5. Política de retenção e arquivamento de conversas/arquivos.

### Fase P2 (excelência operacional)
1. SLOs: tempo de resposta webhook, tempo de processamento de fila, taxa de falha por integração.
2. Estratégia multi-instância Chatwoot com roteamento automático de novas contas.
3. Automação de provisionamento por assinatura com trilha de auditoria completa.
4. Hardening LGPD: consentimento, exportação, anonimização e exclusão segura.

## 8) Recomendação de arquitetura de deploy (alvo)
- Backend API em 2+ réplicas (gunicorn/uvicorn workers) na rede privada.
- RabbitMQ/Redis/Postgres/MinIO em volumes persistentes e backup validado.
- Workers separados por domínio e escalados horizontalmente por fila.
- Cloudflared em container, expondo somente rotas necessárias (API/Chatwoot/admin restrito).
- Frontend na Vercel com variáveis de ambiente por ambiente (preview/prod).
- CI/CD com promotion por estágio e rollback automático.

## 9) Conclusão
O projeto evoluiu bem no núcleo de atendimento, isolamento de tenant e testes críticos do backend.  
Para ficar totalmente pronto para produção “à prova de falhas”, o bloqueio central é infra/orquestração: manifestos Docker inconsistentes, workers legados em composição e integrações ainda parciais.  
A base está pronta para um ciclo de hardening curto e objetivo (P0), seguido de estabilidade/escala (P1).
