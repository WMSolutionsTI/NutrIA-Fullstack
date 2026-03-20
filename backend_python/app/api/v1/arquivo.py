from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.domain.models.arquivo import Arquivo
from app.db import get_db

router = APIRouter()

@router.post("/arquivos/upload")
def upload_arquivo(
    nome: str,
    tipo: str,
    tenant_id: int = None,
    cliente_id: int = None,
    conversa_id: int = None,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Lógica de upload para Minio S3 (mock)
    caminho_s3 = f"s3://minio/{nome}"
    arquivo = Arquivo(
        nome=nome,
        tipo=tipo,
        caminho_s3=caminho_s3,
        tamanho=file.size if hasattr(file, 'size') else None,
        tenant_id=tenant_id,
        cliente_id=cliente_id,
        conversa_id=conversa_id
    )
    db.add(arquivo)
    db.commit()
    db.refresh(arquivo)
    return arquivo

@router.get("/arquivos/{tenant_id}")
def consultar_arquivos(tenant_id: int, db: Session = Depends(get_db)):
    arquivos = db.query(Arquivo).filter(Arquivo.tenant_id == tenant_id).all()
    return arquivos

@router.get("/arquivos/{arquivo_id}/download")
def download_arquivo(arquivo_id: int, db: Session = Depends(get_db)):
    arquivo = db.query(Arquivo).filter(Arquivo.id == arquivo_id).first()
    if not arquivo:
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    # Lógica de download do Minio S3 (mock)
    return {"caminho_s3": arquivo.caminho_s3}