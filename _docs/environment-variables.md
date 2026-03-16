
# 🔐 Estratégia de Variáveis de Ambiente — NutrIA-Pro

## Tiers de Ambiente

| Tier | Branch | Descrição |
|---|---|---|
| `local` | qualquer | Desenvolvimento na máquina do dev |
| `staging` | `develop` | Ambiente de homologação e testes |
| `production` | `main` | Ambiente de produção |

## Regras Fundamentais

1. **NUNCA** commite arquivos `.env` com valores reais
2. Os arquivos `.env` estão no `.gitignore` — verifique antes de commitar
3. Sempre mantenha o `.env.example` atualizado ao adicionar novas variáveis
4. Toda nova variável precisa ser documentada com um comentário

## Estrutura de Arquivos

```
services/
├── api/
│   ├── .env.example    ← commitar (template)
│   └── .env            ← NÃO commitar (valores reais)
├── workers/
│   ├── .env.example    ← commitar (template)
│   └── .env            ← NÃO commitar (valores reais)
└── frontend/
    ├── .env.example    ← commitar (template)
    └── .env.local      ← NÃO commitar (valores reais — Next.js usa .env.local)
```

## Gestão de Secrets por Tier

### Local
- Copie `.env.example` para `.env` e preencha manualmente
- Use senhas simples (ex: `senha123`) — apenas local
- Serviços externos: use sandboxes/ambientes de teste

### Staging
- Secrets armazenados como **GitHub Actions Secrets**
- Injetados automaticamente no deploy via CI/CD
- Nunca ficam em texto plano no repositório

### Production
- Secrets armazenados como **GitHub Actions Secrets** (environment: production)
- Requerem aprovação manual para deploy
- Rotação de secrets a cada 90 dias

## Convenção de Nomenclatura

```
SERVIÇO_FUNCIONALIDADE=valor

# Exemplos:
DATABASE_URL=
REDIS_URL=
CHATWOOT_API_TOKEN=
JWT_SECRET_KEY=
MINIO_ACCESS_KEY=
```

## Variáveis Sensíveis — Nunca em Logs

As seguintes variáveis NUNCA devem aparecer em logs:
- `*_SECRET_KEY`
- `*_PASSWORD`
- `*_API_KEY`
- `*_TOKEN`
- `DATABASE_URL` (contém senha)
