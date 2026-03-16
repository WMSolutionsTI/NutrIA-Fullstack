from minio import Minio
import os

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "nutria-files")

client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False
)

def baixar_arquivo(object_name, local_path):
    client.fget_object(MINIO_BUCKET, object_name, local_path)
    print(f"Arquivo baixado: {object_name} -> {local_path}")
    return local_path

def enviar_arquivo_chatwoot(account_id, conversation_id, local_path):
    """
    Envia arquivo para uma conversa do Chatwoot.
    """
    # TODO: Implementar integração real com Chatwoot (upload de arquivo)
    print(f"Arquivo {local_path} enviado para account {account_id}, conversation {conversation_id} via Chatwoot")
    return True

# Worker pode ser chamado por fila para baixar e enviar arquivos