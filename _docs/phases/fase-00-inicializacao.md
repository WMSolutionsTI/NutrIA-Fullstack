# Fase 00 — Inicialização

> Fundação do projeto: repositório, padrões de código, estrutura de pastas, ADRs iniciais, setup de ferramentas de desenvolvimento.

## Descrição

Esta fase estabelece a fundação técnica e organizacional do projeto NutrIA-Pro. O objetivo é criar um ambiente de desenvolvimento padronizado, com decisões arquiteturais documentadas e ferramentas configuradas, antes de qualquer linha de código de negócio ser escrita.

## Objetivos

- Inicializar repositório GitHub com branch protection e workflows de CI básicos
- Definir estrutura de pastas do monorepo (backend, frontend, workers, docs, projects)
- Estabelecer padrões de código: linters (Ruff, ESLint), formatadores (Black, Prettier), pre-commit hooks
- Documentar ADRs (Architecture Decision Records) iniciais
- Configurar ferramentas de desenvolvimento: Docker Compose local, Makefile, scripts de seed

## Entregas

- Repositório estruturado e padronizado
- ADRs documentados para decisões arquiteturais chave
- Ambiente de desenvolvimento local funcional com `make dev`
- CI básico rodando linters e testes no GitHub Actions

## Referência

Ver `projects/fase-00-inicializacao.yaml` para issues detalhadas.
