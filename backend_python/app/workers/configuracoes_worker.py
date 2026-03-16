import psycopg2
import os

def criar_tabelas():
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cur = conn.cursor()
      # Removido: tabelas n8n_* migradas para workers Python
    conn.commit()
    cur.close()
    conn.close()

def get_chatwoot_config():
  return {
    "url_chatwoot": os.getenv("CHATWOOT_URL", "http://chatwoot:3000"),
    "id_conta": os.getenv("CHATWOOT_ID_CONTA", "1")
  }

if __name__ == "__main__":
    criar_tabelas()
    print(f"Configuração inicial concluída. Chatwoot: {url_chatwoot}, Conta: {id_conta}")