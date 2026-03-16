from fpdf import FPDF
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

def gerar_pdf_plano(cliente_nome: str, plano: str, arquivo_nome: str):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=16)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(200, 10, txt=f"Plano Alimentar Personalizado para {cliente_nome}", ln=True, align="C")
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, plano)
    pdf.set_font("Arial", size=10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, txt="Siga este plano para alcançar seus objetivos!", ln=True, align="C")
    pdf.output(arquivo_nome)
    client.fput_object(MINIO_BUCKET, arquivo_nome, arquivo_nome)
    return arquivo_nome

# Mock: função para enviar arquivo via Chatwoot

def enviar_pdf_chatwoot(account_id: int, conversation_id: int, arquivo_nome: str):
    # TODO: Implementar integração real com Chatwoot (upload de arquivo PDF)
    return True