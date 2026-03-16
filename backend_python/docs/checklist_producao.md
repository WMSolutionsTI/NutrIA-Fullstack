# Checklist de Validação de Produção — NutrIA-Pro

## Infraestrutura
- [ ] Docker Compose com recursos limitados (memória, CPU)
- [ ] Healthchecks configurados para todos serviços
- [ ] Rede interna Docker, sem portas expostas
- [ ] Cloudflare Tunnel ativo e seguro
- [ ] Nginx com rate limiting, gzip, client_max_body_size

## Backend (FastAPI)
- [ ] Gunicorn/Uvicorn com workers ajustados conforme CPU
- [ ] CORSMiddleware configurado para domínio nutriapro.com.br
- [ ] Logging estruturado e níveis configuráveis
- [ ] .env com variáveis de produção (chaves, brokers, paths)
- [ ] Endpoints versionados e documentados

## Workers e Filas
- [ ] Celery com RabbitMQ e Redis
- [ ] Filas especializadas, DLQ configurada
- [ ] Workers replicados conforme demanda
- [ ] Monitoramento RabbitMQ (interface web)

## Observabilidade
- [ ] Logs centralizados (Loguru/Sentry)
- [ ] Métricas expostas (Prometheus/Grafana)
- [ ] Alertas para falhas críticas

## Testes e Performance
- [ ] Testes automatizados (pytest, cobertura)
- [ ] Teste de carga (locust, k6)
- [ ] Monitoramento de latência, throughput, erros

## Segurança
- [ ] JWT seguro, refresh token implementado
- [ ] Segredos e chaves fora do repositório
- [ ] Nginx sem exposição de versão
- [ ] Rate limiting para endpoints sensíveis

## Frontend
- [ ] Variáveis de ambiente corretas (API URL, tokens)
- [ ] Middleware de proteção de rotas
- [ ] Integração com backend validada

---

> Use este checklist antes de cada deploy para garantir robustez, escalabilidade e segurança em produção.
