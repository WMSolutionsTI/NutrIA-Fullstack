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


def upload_object(object_name: str, file_path: str):
    try:
        client.fput_object(MINIO_BUCKET, object_name, file_path)
        print(f"Uploaded {object_name} to {MINIO_BUCKET}")
        return True
    except Exception:
        return False


def download_object(object_name: str, file_path: str):
    try:
        client.fget_object(MINIO_BUCKET, object_name, file_path)
        return True
    except Exception:
        return False


def list_objects():
    try:
        return [obj.object_name for obj in client.list_objects(MINIO_BUCKET)]
    except Exception:
        return []
