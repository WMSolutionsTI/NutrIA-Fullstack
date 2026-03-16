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

    client.fput_object(MINIO_BUCKET, object_name, file_path)
    print(f"Uploaded {object_name} to {MINIO_BUCKET}")

    client.fget_object(MINIO_BUCKET, object_name, file_path)
    # Worker pode ser chamado por fila para download

    return [obj.object_name for obj in client.list_objects(MINIO_BUCKET)]