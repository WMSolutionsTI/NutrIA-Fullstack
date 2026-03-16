# Worker: monitor_app_worker.py

Este worker monitora toda a aplicação NutrIA-Pro, coletando métricas, logs, eventos, novidades, dicas e problemas, e envia relatórios automáticos para o administrador via Chatwoot.

## Funcionalidade
- Coleta métricas de uso, erros, eventos críticos e tópicos configurados.
- Envia mensagens automáticas para a inbox do administrador no Chatwoot.
- Permite configurar frequência de envio e tópicos monitorados via variáveis de ambiente.

## Variáveis de Ambiente
- `CHATWOOT_ADMIN_INBOX_ID`: ID da inbox do admin no Chatwoot.
- `CHATWOOT_API_URL`: URL da API do Chatwoot.
- `CHATWOOT_API_KEY`: Token de acesso à API do Chatwoot.
- `MONITOR_INTERVAL`: Intervalo (segundos) entre envios automáticos (default: 600).
- `LOG_PATH`: Caminho do arquivo de log para análise (default: /app/logs/nutria-backend.log).
- `TOPICS_MONITOR`: Lista de tópicos monitorados, separados por vírgula (ex: novidades,problemas,dicas,ajustes,erros,backup).

## Exemplo de Execução
```bash
python app/workers/monitor_app_worker.py
```

## Exemplo de Serviço no Docker Compose
```yaml
  worker_monitor:
    build: ../backend_python
    command: python app/workers/monitor_app_worker.py
    environment:
      - CHATWOOT_ADMIN_INBOX_ID=1
      - CHATWOOT_API_URL=https://chatwoot.example.com/api/v1
      - CHATWOOT_API_KEY=seu_token
      - MONITOR_INTERVAL=600
      - LOG_PATH=/app/logs/nutria-backend.log
      - TOPICS_MONITOR=novidades,problemas,dicas,ajustes,erros,backup
    depends_on:
      - backend
      - rabbitmq
    networks:
      - messaging_net
    deploy:
      replicas: 1
      resources:
        limits:
          cpus: '0.25'
          memory: 256M
        reservations:
          cpus: '0.10'
          memory: 128M
```

## Customização
- Adicione integração com Prometheus, healthchecks, ou outras fontes de métricas conforme necessidade.
- Personalize tópicos monitorados via variável `TOPICS_MONITOR`.
- Ajuste frequência de envio com `MONITOR_INTERVAL`.

## Testes
- Verifique se mensagens chegam à inbox do admin no Chatwoot.
- Simule eventos críticos e erros para validar alertas.
- Ajuste variáveis de ambiente e monitore o comportamento.

---
Desenvolvido para garantir visibilidade, proatividade e segurança operacional no NutrIA-Pro.