import psycopg2
import os

DATABASE_URL = os.getenv("DATABASE_URL")

def buscar_mensagens(telefone):
    """
    Busca mensagens na fila por telefone.
    """
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    # Removido: uso de n8n_fila_mensagens. Use fila/DB própria do worker.
    conn.close()
    return mensagens

def limpar_fila_mensagens(telefone):
    """
    Limpa fila de mensagens por telefone.
    """
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    # Removido: uso de n8n_fila_mensagens. Use fila/DB própria do worker.
    cur.close()
    conn.close()

def mensagem_encavalada(ultima_id, workflow_id):
    """
    Verifica se há mensagem encavalada.
    """
    return ultima_id != workflow_id

def process_secretaria_v3(telefone, workflow_id):
    """
    Processa fila secretaria_v3 para workers de fila.
    """
    mensagens = buscar_mensagens(telefone)
    if not mensagens:
        return []
    ultima_id = mensagens[-1][1]  # id_mensagem
    if mensagem_encavalada(ultima_id, workflow_id):
        return []  # Mensagem encavalada, para o workflow
    limpar_fila_mensagens(telefone)
    # Removido: retorno de mensagens n8n. Adapte para retorno do worker.