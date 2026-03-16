## 📋 Descrição

<!-- Descreva claramente o que foi feito neste PR -->

## 🎯 Tipo de Mudança

<!-- Marque com [x] o que se aplica -->

- [ ] `feat` — Nova funcionalidade
- [ ] `fix` — Correção de bug
- [ ] `refactor` — Refatoração sem mudança de comportamento
- [ ] `chore` — Dependências ou configurações
- [ ] `docs` — Apenas documentação
- [ ] `test` — Testes
- [ ] `ci` — CI/CD

## 🔗 Issue Relacionada

<!-- Ex: Closes #42 ou Relates to #15 -->

Closes #

## 🧪 Como Testar

<!-- Descreva os passos para testar as mudanças -->

1.
2.
3.

## ✅ Checklist

### Obrigatório
- [ ] Pre-commit passa sem erros (`pre-commit run --all-files`)
- [ ] Testes unitários escritos e passando
- [ ] Cobertura de testes não reduziu abaixo de 80%
- [ ] Nenhum `secret` ou credencial no código
- [ ] `tenant_id` presente em todos os novos modelos e queries (se aplicável)

### Backend (se aplicável)
- [ ] `ruff check .` sem erros
- [ ] `black .` aplicado
- [ ] `mypy app/` sem erros
- [ ] Migration criada e é backward compatible
- [ ] Migration testada: `upgrade head` e `downgrade -1`

### Frontend (se aplicável)
- [ ] `npm run lint` sem erros
- [ ] `npm run format:check` sem erros
- [ ] `npm run type-check` sem erros

### Infraestrutura (se aplicável)
- [ ] `docker compose up` sobe sem erros
- [ ] Variáveis de ambiente documentadas no `.env.example`

## 📸 Screenshots (se aplicável)

<!-- Adicione screenshots para mudanças visuais no frontend -->

## 📝 Notas para o Revisor

<!-- Algum contexto adicional, decisões técnicas ou pontos de atenção -->
