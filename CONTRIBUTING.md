# 🤝 Guia de Contribuição — NutrIA-Pro

Obrigado por contribuir com o NutrIA-Pro! Este guia define os padrões e fluxos de trabalho do projeto.

---

## 📋 Índice

- [Pré-requisitos](#pré-requisitos)
- [Configurando o Ambiente](#configurando-o-ambiente)
- [Fluxo de Desenvolvimento](#fluxo-de-desenvolvimento)
- [Padrões de Commit](#padrões-de-commit)
- [Padrões de Branch](#padrões-de-branch)
- [Abrindo um Pull Request](#abrindo-um-pull-request)
- [Padrões de Código](#padrões-de-código)
- [Rodando os Testes](#rodando-os-testes)

---

## ✅ Pré-requisitos

- Docker >= 24.x
- Docker Compose V2 >= 2.x
- Python >= 3.12
- Node.js >= 20.x
- Git >= 2.x

---

## ⚙️ Configurando o Ambiente

```bash
# 1. Clone o repositório
git clone https://github.com/WMSolutionsTI/NutrIA-Pro.git
cd NutrIA-Pro

# 2. Instale o pre-commit
pip install pre-commit
pre-commit install

# 3. Configure as variáveis de ambiente
cp services/api/.env.example services/api/.env
cp services/frontend/.env.example services/frontend/.env

# 4. Suba os serviços
docker compose up -d

# 5. Execute as migrations
docker compose exec api alembic upgrade head
```

---

## 🔄 Fluxo de Desenvolvimento

```
main (produção)
  └── develop (integração)
        └── feat/api/nome-da-feature     ← você trabalha aqui
        └── feat/frontend/nome-da-feature
        └── fix/worker/descricao-do-bug
```

### Passo a passo

```bash
# 1. Sempre parta da develop atualizada
git checkout develop
git pull origin develop

# 2. Crie sua branch
git checkout -b feat/api/nome-da-feature

# 3. Desenvolva e commite
git add .
git commit -m "feat(api): descrição clara do que foi feito"

# 4. Envie para o GitHub
git push origin feat/api/nome-da-feature

# 5. Abra um Pull Request para develop no GitHub
```

---

## 📝 Padrões de Commit

O projeto usa [Conventional Commits](https://www.conventionalcommits.org/).

### Formato

```
<tipo>(<escopo>): <descrição curta em minúsculas>
```

### Tipos permitidos

| Tipo | Quando usar |
|---|---|
| `feat` | Nova funcionalidade |
| `fix` | Correção de bug |
| `chore` | Dependências, configurações |
| `docs` | Apenas documentação |
| `test` | Testes |
| `refactor` | Refatoração sem mudança de comportamento |
| `perf` | Melhoria de performance |
| `ci` | Mudanças no CI/CD |

### Escopos comuns

`api` · `worker` · `frontend` · `infra` · `db` · `auth` · `tooling`

### Exemplos

```bash
git commit -m "feat(api): adiciona endpoint de agendamento de consultas"
git commit -m "fix(worker): corrige retry em falha de conexão com RabbitMQ"
git commit -m "docs(readme): atualiza instruções de instalação"
git commit -m "test(api): adiciona testes de isolamento multi-tenant"
git commit -m "chore(infra): atualiza versão do PostgreSQL para 16"
```

---

## 🌿 Padrões de Branch

```
feat/<escopo>/<descricao-com-hifens>
fix/<escopo>/<descricao-com-hifens>
chore/<escopo>/<descricao-com-hifens>
docs/<descricao-com-hifens>
```

### Exemplos

```
feat/api/endpoint-agendamento
feat/frontend/tela-login
fix/worker/retry-rabbitmq
chore/infra/upgrade-postgres-16
docs/contributing-guide
```

---

## 🔀 Abrindo um Pull Request

1. Certifique-se de que todos os testes passam localmente
2. Certifique-se de que o pre-commit passa sem erros
3. Abra o PR **sempre para `develop`** — nunca direto para `main`
4. Preencha o template de PR completamente
5. Aguarde pelo menos 1 aprovação antes de fazer merge

---

## 🎨 Padrões de Código

### Python (Backend)

```bash
cd services/api

# Verificar problemas
ruff check .

# Corrigir automaticamente
ruff check . --fix

# Formatar
black .

# Verificar tipos
mypy app/
```

### TypeScript (Frontend)

```bash
cd services/frontend

# Verificar problemas
npm run lint

# Corrigir automaticamente
npm run lint:fix

# Formatar
npm run format

# Verificar tipos
npm run type-check
```

---

## 🧪 Rodando os Testes

```bash
# Todos os testes
make test

# Apenas unitários
docker compose exec api pytest tests/unit/ -v

# Apenas integração
docker compose exec api pytest tests/integration/ -v

# Com cobertura
docker compose exec api pytest --cov=app --cov-report=html
```

> ⚠️ O CI bloqueia merges quando a cobertura cai abaixo de **80%**.
