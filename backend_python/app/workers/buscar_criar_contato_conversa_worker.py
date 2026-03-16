import psycopg2
import os

DATABASE_URL = os.getenv("DATABASE_URL")

# Função para buscar ou criar contato e conversa

def buscar_ou_criar_contato_conversa(telefone, nome):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    # Buscar contato
    cur.execute("SELECT id FROM clientes WHERE contato_chatwoot=%s", (telefone,))
    contato = cur.fetchone()
    if not contato:
        # Criar contato
        cur.execute("INSERT INTO clientes (nome, contato_chatwoot) VALUES (%s, %s) RETURNING id", (nome, telefone))
        contato_id = cur.fetchone()[0]
        conn.commit()
    else:
        contato_id = contato[0]
    # Buscar conversa
    cur.execute("SELECT id FROM conversas WHERE cliente_id=%s ORDER BY id DESC LIMIT 1", (contato_id,))
    conversa = cur.fetchone()
    if not conversa:
        cur.execute("INSERT INTO conversas (cliente_id, mensagem) VALUES (%s, %s) RETURNING id", (contato_id, "Início de conversa"))
        conversa_id = cur.fetchone()[0]
        conn.commit()
    else:
        conversa_id = conversa[0]
    cur.close()
    conn.close()
    return {"contato_id": contato_id, "conversa_id": conversa_id}

# Exemplo de uso:
if __name__ == "__main__":
    telefone = "+5511999999999"
    nome = "Cliente Teste"
    resultado = buscar_ou_criar_contato_conversa(telefone, nome)
    print("Contato e conversa:", resultado)