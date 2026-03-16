# Fase 01 — Infraestrutura

> Provisionamento de toda a infraestrutura: VPS/cloud, Docker Compose, PostgreSQL com replicação primário/réplica, Redis, RabbitMQ, Chatwoot, n8n, Traefik, DNS e SSL.

## Descrição

Esta fase provisiona toda a infraestrutura necessária para rodar o NutrIA-Pro em produção. Inclui configuração de servidores, contêineres, bancos de dados com estratégia de leitura/escrita segregada, broker de mensagens, e todas as ferramentas de plataforma.

## Stack de Infraestrutura

| Componente | Tecnologia | Função |
|-----------|-----------|--------|
| Runtime | Docker Compose | Orquestração de contêineres |
| Banco de Dados (escrita) | PostgreSQL 16 Primary | Writes exclusivos — INSERT/UPDATE/DELETE |
| Banco de Dados (leitura) | PostgreSQL 16 Replica | Reads — queries de consulta, relatórios, anamnese |
| Connection Pooling | PgBouncer | Pool de conexões, roteamento read/write |
| Cache/Sessão | Redis 7 | Cache, sessões, idempotência, filas temporárias |
| Message Broker | RabbitMQ 3.13 | Filas de workers |
| Chat Hub | Chatwoot | Gerenciamento de conversas |
| Automação | n8n | Engine de workflows |
| Proxy | Traefik | Reverse proxy, SSL automático |
| Armazenamento | MinIO | Arquivos, PDFs de planos alimentares, anexos |
| STT/TTS | Retell AI / Whisper | Transcrição de áudio para anamnese por voz |

## Objetivos

- Provisionar VPS/cloud com Docker Engine e Docker Compose
- Configurar `docker-compose.yml` de produção com todos os serviços
- **Configurar PostgreSQL Primary com streaming replication para Replica de leitura**
- **Configurar PgBouncer para roteamento automático: writes → primary, reads → replica**
- Configurar Redis com persistência e autenticação
- Deploy e configuração inicial do Chatwoot (inbox WhatsApp via Evolution API)
- Deploy e configuração inicial do n8n (PostgreSQL backend, autenticação)
- Configurar Traefik com Let's Encrypt para SSL automático
- Configurar DNS para todos os subdomínios
- **Configurar bucket MinIO dedicado para PDFs de planos alimentares por tenant**
- **Configurar integração STT (Speech-to-Text) para anamnese por voz**

## Estratégia Anti-Travamento

- PostgreSQL Primary → somente escrita (nunca usado para SELECT de leitura)
- PostgreSQL Replica → somente leitura (relatórios, anamnese, histórico)
- PgBouncer em modo transaction pooling (mínimo de conexões abertas)
- Redis para cache de dados quentes (configurações de tenant, prontuários ativos)
- RabbitMQ com prefetch_count controlado por fila (backpressure automático)

## Referência

Ver `projects/fase-01-infraestrutura.yaml` para issues detalhadas.
