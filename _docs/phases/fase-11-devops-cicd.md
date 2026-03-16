# Fase 11 — DevOps e CI/CD

> Pipeline CI/CD com GitHub Actions: testes automatizados, build Docker, deploy blue-green, rollback automático, ambientes staging/production.

## Descrição

Esta fase implementa o pipeline completo de CI/CD para automação de testes, builds e deploys do NutrIA-Pro, garantindo qualidade e rapidez nas entregas.

## Pipeline CI/CD

### CI (Continuous Integration)
- Lint e formatação (Ruff, Black, ESLint, Prettier)
- Testes unitários e de integração (pytest, Jest)
- Build das imagens Docker
- Scan de vulnerabilidades (Trivy)
- Code coverage mínimo de 80%

### CD (Continuous Deployment)
- Deploy automático para staging em merge na branch `develop`
- Deploy para produção com aprovação manual (ou automático em `main`)
- **Blue-Green Deployment:** zero downtime, troca de tráfego via Traefik
- Smoke tests pós-deploy automáticos
- Rollback automático se smoke tests falharem

## Ambientes

| Ambiente | Branch | Deploy | URL |
|----------|--------|--------|-----|
| Development | feature/* | Manual | localhost |
| Staging | develop | Automático | staging.nutrisaas.com |
| Production | main | Aprovação manual | app.nutrisaas.com |

## Referência

Ver `projects/fase-11-devops-cicd.yaml` para issues detalhadas.
