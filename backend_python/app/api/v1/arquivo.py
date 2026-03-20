from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.domain.models.arquivo import Arquivo
from app.domain.models.cliente import Cliente
from app.db import get_db
from app.services.ai_service import gerar_resposta_agente
from app.workers.minio_worker import upload_object, download_object
from app.workers.chatwoot_attachment_worker import enviar_arquivo_chatwoot
import os
import uuid

router = APIRouter()

@router.post("/arquivos/upload")
def upload_arquivo(
    nome: str,
    tipo: str,
    tenant_id: int,
    descricao: str = "",
    cliente_id: int = None,
    conversa_id: int = None,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    local_path = f"/tmp/{uuid.uuid4()}_{file.filename}"
    with open(local_path, "wb") as f:
        f.write(file.file.read())

    object_name = f"{tenant_id}/{uuid.uuid4()}_{file.filename}"
    if not upload_object(object_name, local_path):
        raise HTTPException(status_code=500, detail="Falha ao enviar arquivo para Minio")

    caminho_s3 = object_name
    arquivo = Arquivo(
        nome=nome,
        tipo=tipo,
        caminho_s3=caminho_s3,
        tamanho=os.path.getsize(local_path),
        tenant_id=tenant_id,
        cliente_id=cliente_id,
        conversa_id=conversa_id
    )
    db.add(arquivo)
    db.commit()
    db.refresh(arquivo)

    os.remove(local_path)

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

    return {
        "status": "ok",
        "sugestao_ia": resposta_ia,
        "arquivo": arquivo.nome,
        "cliente": cliente.nome
    }

@router.post("/arquivos/repository/enviar_cliente")
def enviar_arquivo_repository_para_cliente(
    arquivo_id: int,
    cliente_id: int,
    account_id: str,
    conversation_id: str,
    db: Session = Depends(get_db)
):
    arquivo = db.query(Arquivo).filter(Arquivo.id == arquivo_id).first()
    if not arquivo:
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")

    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    local_path = f"/tmp/{uuid.uuid4()}_{arquivo.nome}"
    if not download_object(arquivo.caminho_s3, local_path):
        raise HTTPException(status_code=500, detail="Falha ao baixar arquivo do Minio")

    enviado = enviar_arquivo_chatwoot(account_id, conversation_id, local_path)
    os.remove(local_path)

    if not enviado:
        raise HTTPException(status_code=500, detail="Falha ao enviar arquivo para Chatwoot")

    prompt = f"Envie o arquivo '{arquivo.nome}' para o cliente '{cliente.nome}' com instruções de uso e contexto: {arquivo.tipo}."
    sugestao = gerar_resposta_agente("suporte_nutri", prompt, contexto=arquivo.tipo)

    return {
        "status": "enviado",
        "sugestao_ia": sugestao,
        "cliente": cliente.nome,
        "arquivo": arquivo.nome
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