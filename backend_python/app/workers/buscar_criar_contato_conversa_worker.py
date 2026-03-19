import psycopg2
import os

DATABASE_URL = os.getenv("DATABASE_URL")

# Função para buscar ou criar contato e conversa

def buscar_ou_criar_contato_conversa(telefone, nome):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    # Buscar caixa de entrada e nutricionista pelo inbox_id
    # inbox_id deve ser passado como argumento adicional
    def buscar_nutricionista_por_inbox(inbox_id):
        cur.execute("SELECT nutricionista_id FROM caixas_de_entrada WHERE identificador_chatwoot=%s", (inbox_id,))
        result = cur.fetchone()
        return result[0] if result else None

    # Buscar contato
    cur.execute("SELECT id FROM clientes WHERE contato_chatwoot=%s", (telefone,))
    contato = cur.fetchone()
    if not contato:
        # Vincular ao nutricionista
        inbox_id = os.getenv("INBOX_ID")  # inbox_id deve ser passado ou setado no ambiente
        nutricionista_id = buscar_nutricionista_por_inbox(inbox_id)
        # Criar contato com vínculo
        cur.execute("INSERT INTO clientes (nome, contato_chatwoot, status, nutricionista_id) VALUES (%s, %s, %s, %s) RETURNING id", (nome, telefone, "cliente_potencial", nutricionista_id))
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