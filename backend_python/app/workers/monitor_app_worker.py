import os
import time
import requests
from app.core.logging import logger

CHATWOOT_ADMIN_INBOX_ID = os.getenv("CHATWOOT_ADMIN_INBOX_ID")
CHATWOOT_API_URL = os.getenv("CHATWOOT_API_URL", "https://chatwoot.example.com/api/v1")
CHATWOOT_API_KEY = os.getenv("CHATWOOT_API_KEY")

MONITOR_INTERVAL = int(os.getenv("MONITOR_INTERVAL", "600"))  # 10 min padrão

# Exemplos de coleta de métricas (substitua por integrações reais)
def get_app_metrics():
    log_path = os.getenv("LOG_PATH", "/app/logs/nutria-backend.log")
    errors_last_hour = 0
    events = []
    topics_monitor = os.getenv("TOPICS_MONITOR", "novidades,problemas,dicas,ajustes,erros,backup").split(",")
    try:
        with open(log_path, "r") as f:
            lines = f.readlines()
            for line in lines[-500:]:
                if "ERROR" in line:
                    errors_last_hour += 1
                if "CRITICAL" in line:
                    events.append(line.strip())
    except Exception as e:
        logger.error("Erro ao ler logs para monitoramento", extra={"error": str(e)})
    return {
        "cpu_usage": "20%",  # TODO: integrar coleta real
        "memory_usage": "1.2GB",  # TODO: integrar coleta real
        "active_workers": 5,  # TODO: integrar coleta real
        "errors_last_hour": errors_last_hour,
        "events": events,
        "topics_monitor": topics_monitor,
        "new_features": ["Novo endpoint de agendamento", "Worker de backup automático"],
        "tips": ["Aumente replicas do worker_secretaria para alta demanda.", "Configure alertas de backup."]
    }

def send_message_to_admin(subject, content):
    url = f"{CHATWOOT_API_URL}/inboxes/{CHATWOOT_ADMIN_INBOX_ID}/messages"
    headers = {"api_access_token": CHATWOOT_API_KEY, "Content-Type": "application/json"}
    data = {
        "content": f"[{subject}]\n{content}"
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        logger.info("Mensagem enviada ao admin Chatwoot", extra={"data": response.json()})
    else:
        logger.error("Erro ao enviar mensagem ao admin Chatwoot", extra={"error": response.text})


def main():
    while True:
        metrics = get_app_metrics()
        subject = "Atualização automática NutrIA-Pro"
        content = f"CPU: {metrics['cpu_usage']}\nMemória: {metrics['memory_usage']}\nWorkers ativos: {metrics['active_workers']}\nErros última hora: {metrics['errors_last_hour']}\nTópicos monitorados: {', '.join(metrics['topics_monitor'])}\nNovidades: {', '.join(metrics['new_features'])}\nDicas: {', '.join(metrics['tips'])}"
        if metrics['events']:
            content += f"\nEventos críticos recentes:\n" + "\n".join(metrics['events'])
        send_message_to_admin(subject, content)
        time.sleep(MONITOR_INTERVAL)

if __name__ == "__main__":
    main()
