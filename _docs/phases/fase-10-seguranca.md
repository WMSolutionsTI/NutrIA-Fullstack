# Fase 10 — Segurança

> Hardening de segurança: rate limiting, validação de webhooks (HMAC), auditoria de ações, criptografia de dados sensíveis (prompts de IA, credenciais de integração), pentest.

## Descrição

Esta fase implementa o hardening de segurança do NutrIA-Pro, garantindo proteção de dados dos clientes e nutricionistas, validação de todos os webhooks externos, e rastreabilidade completa de ações sensíveis.

## Áreas de Segurança

### Autenticação e Autorização
- Rate limiting por IP e por tenant (Redis sliding window)
- Proteção de rotas internas com `X-Internal-API-Key` (não JWT)
- Rotação periódica de tokens e API keys

### Validação de Webhooks
- Verificação HMAC-SHA256 em todos os webhooks externos (Chatwoot, Asaas, Retell)
- Rejeição de requisições com timestamp > 5 minutos (anti-replay)
- Whitelist de IPs para webhooks críticos

### Criptografia de Dados Sensíveis
- Prompts de IA dos nutricionistas criptografados em repouso (AES-256)
- Credenciais OAuth (Google, Asaas) criptografadas no banco
- Chaves de API criptografadas com per-tenant encryption key

### Auditoria
- Log imutável de todas as ações administrativas
- Rastreamento de acesso a dados de clientes
- Registro de todas as intervenções humanas no agente de IA

## Referência

Ver `projects/fase-10-seguranca.yaml` para issues detalhadas.
