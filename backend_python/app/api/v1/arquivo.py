from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.domain.models.arquivo import Arquivo
from app.domain.models.cliente import Cliente
from app.db import get_db
from app.services.ai_service import gerar_resposta_agente

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

@router.post("/arquivos/enviar_ia")
def enviar_arquivo_ia(file_id: int, cliente_id: int, contexto: str = None, db: Session = Depends(get_db)):
    arquivo = db.query(Arquivo).filter(Arquivo.id == file_id).first()
    if not arquivo:
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")

    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    prompt_usuario = (
        f"O arquivo '{arquivo.nome}' (tipo {arquivo.tipo}) foi enviado para o cliente {cliente.nome} (status {cliente.status}). "
        f"Contexto do nutricionista: {contexto or 'não informado'}. "
        "Gere a mensagem mais apropriada para enviar ao cliente com base nesse arquivo e contexto, como um assistente de nutricionista experiente."
    )

    resposta_ia = gerar_resposta_agente("suporte_nutri", prompt_usuario, contexto=contexto)

    # Simulação de envio - em um ambiente real, enviar via Chatwoot ou worker de mensagens.
    return {
        "status": "ok",
        "sugestao_ia": resposta_ia,
        "arquivo": arquivo.nome,
        "cliente": cliente.nome
    }

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