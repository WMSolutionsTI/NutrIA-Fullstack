from datetime import datetime
import hashlib
import os
import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api.v1.auth import get_current_user
from app.db import get_db
from app.domain.models.arquivo import Arquivo
from app.domain.models.arquivo_dispatch import ArquivoDispatch
from app.domain.models.avanco import Avanco
from app.domain.models.cliente import Cliente
from app.domain.models.nutricionista import Nutricionista
from app.services.ai_service import gerar_resposta_agente
from app.services.event_bus import build_event_payload, publish_event
from app.services.ocr_service import extract_text_from_file
from app.services.worker_job_service import create_worker_job
from app.workers.chatwoot_attachment_worker import enviar_arquivo_chatwoot
from app.workers.minio_worker import download_object, upload_object

router = APIRouter()

ALLOWED_FILE_TYPES = {"documento", "imagem", "audio", "video"}


def _registrar_avanco_ocr(
    db: Session, *, arquivo: Arquivo, current_user: Nutricionista, ocr_texto: str
) -> None:
    if not arquivo.cliente_id or not ocr_texto:
        return
    db.add(
        Avanco(
            cliente_id=arquivo.cliente_id,
            nutricionista_id=current_user.id,
            data=datetime.utcnow(),
            descricao=f"[OCR_ARQUIVO] {arquivo.nome}\n{ocr_texto[:2000]}",
            status="concluido",
        )
    )
    db.commit()


def _processar_ocr_arquivo(
    db: Session,
    *,
    arquivo: Arquivo,
    local_path: str,
    current_user: Nutricionista,
    registrar_avanco: bool = True,
) -> dict:
    result = extract_text_from_file(local_path, filename=arquivo.nome)
    arquivo.ocr_status = result.status
    arquivo.ocr_engine = result.engine
    arquivo.ocr_texto = result.text[:8000] if result.text else None
    arquivo.ocr_extraido_em = datetime.utcnow()
    db.add(arquivo)
    db.commit()
    db.refresh(arquivo)

    if registrar_avanco and result.status == "ok" and result.text:
        _registrar_avanco_ocr(db, arquivo=arquivo, current_user=current_user, ocr_texto=result.text)

    return {
        "ocr_status": result.status,
        "ocr_engine": result.engine,
        "ocr_detail": result.detail,
        "ocr_texto_preview": (result.text or "")[:500],
    }


@router.post("/arquivos/upload")
def upload_arquivo(
    nome: str = Form(...),
    tipo: str = Form(...),
    tenant_id: int | None = Form(default=None),
    descricao: str = Form(default=""),
    cliente_id: int | None = Form(default=None),
    conversa_id: int | None = Form(default=None),
    caixa_id: int | None = Form(default=None),
    account_id: str | None = Form(default=None),
    conversation_id: str | None = Form(default=None),
    executar_ocr: bool = Form(default=True),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Nutricionista = Depends(get_current_user),
):
    tipo_norm = tipo.strip().lower()
    if tipo_norm not in ALLOWED_FILE_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Tipo de arquivo inválido. Use: documento, imagem, audio ou video.",
        )

    tenant_resolved = tenant_id or current_user.tenant_id
    if not tenant_resolved:
        raise HTTPException(status_code=400, detail="tenant_id não encontrado para upload.")
    if current_user.papel != "admin" and tenant_resolved != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="Acesso negado")

    local_path = f"/tmp/{uuid.uuid4()}_{file.filename}"
    file_bytes = file.file.read()
    with open(local_path, "wb") as f:
        f.write(file_bytes)

    object_name = f"{tenant_resolved}/{uuid.uuid4()}_{file.filename}"
    if not upload_object(object_name, local_path):
        raise HTTPException(status_code=500, detail="Falha ao enviar arquivo para Minio")

    hash_sha256 = hashlib.sha256(file_bytes).hexdigest()
    arquivo = Arquivo(
        nome=nome,
        tipo=tipo_norm,
        caminho_s3=object_name,
        tamanho=os.path.getsize(local_path),
        tenant_id=tenant_resolved,
        cliente_id=cliente_id,
        conversa_id=conversa_id,
        criado_em=datetime.utcnow(),
    )
    db.add(arquivo)
    db.commit()
    db.refresh(arquivo)

    ocr_payload = {
        "ocr_status": "ignored",
        "ocr_engine": None,
        "ocr_detail": "OCR não aplicável para este tipo de arquivo.",
        "ocr_texto_preview": "",
    }
    if executar_ocr and tipo_norm in {"documento", "imagem"}:
        ocr_payload = _processar_ocr_arquivo(
            db,
            arquivo=arquivo,
            local_path=local_path,
            current_user=current_user,
            registrar_avanco=True,
        )

    os.remove(local_path)

    dispatch = None
    if account_id and conversation_id:
        dispatch = ArquivoDispatch(
            arquivo_id=arquivo.id,
            tenant_id=tenant_resolved,
            nutricionista_id=current_user.id,
            cliente_id=cliente_id,
            caixa_id=caixa_id,
            account_id=account_id,
            conversation_id=conversation_id,
            mime_type=file.content_type,
            sha256=hash_sha256,
            status="queued",
            tentativas=0,
            criado_em=datetime.utcnow(),
            atualizado_em=datetime.utcnow(),
        )
        db.add(dispatch)
        db.commit()
        db.refresh(dispatch)

        event = build_event_payload(
            queue_tipo="arquivo_dispatch",
            tenant_id=tenant_resolved,
            nutricionista_id=current_user.id,
            cliente_id=cliente_id,
            payload={"arquivo_dispatch_id": dispatch.id, "arquivo_id": arquivo.id},
        )
        publish_event("queue.arquivo.dispatch", event)
        create_worker_job(
            db,
            event_id=event["event_id"],
            queue="queue.arquivo.dispatch",
            tipo="arquivo_dispatch",
            tenant_id=tenant_resolved,
            nutricionista_id=current_user.id,
            cliente_id=cliente_id,
            payload=event,
        )

    return {
        "id": arquivo.id,
        "nome": arquivo.nome,
        "tipo": arquivo.tipo,
        "caminho_s3": arquivo.caminho_s3,
        "tamanho": arquivo.tamanho,
        "dispatch_id": dispatch.id if dispatch else None,
        "dispatch_status": dispatch.status if dispatch else None,
        "descricao": descricao,
        **ocr_payload,
    }


@router.post("/arquivos/enviar_ia")
def enviar_arquivo_ia(
    file_id: int,
    cliente_id: int,
    contexto: str | None = None,
    db: Session = Depends(get_db),
    current_user: Nutricionista = Depends(get_current_user),
):
    arquivo = db.query(Arquivo).filter(Arquivo.id == file_id).first()
    if not arquivo:
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    if current_user.papel != "admin" and arquivo.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="Acesso negado")

    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    if current_user.papel != "admin" and cliente.nutricionista_id != current_user.id:
        raise HTTPException(status_code=403, detail="Acesso negado")

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
        "cliente": cliente.nome,
    }


@router.post("/arquivos/repository/enviar_cliente")
def enviar_arquivo_repository_para_cliente(
    arquivo_id: int,
    cliente_id: int,
    account_id: str,
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: Nutricionista = Depends(get_current_user),
):
    arquivo = db.query(Arquivo).filter(Arquivo.id == arquivo_id).first()
    if not arquivo:
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    if current_user.papel != "admin" and arquivo.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="Acesso negado")

    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    if current_user.papel != "admin" and cliente.nutricionista_id != current_user.id:
        raise HTTPException(status_code=403, detail="Acesso negado")

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
        "arquivo": arquivo.nome,
    }


@router.get("/arquivos/repository/{tenant_id}")
def consultar_arquivos_repository(
    tenant_id: int,
    db: Session = Depends(get_db),
    current_user: Nutricionista = Depends(get_current_user),
):
    if current_user.papel != "admin" and tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="Acesso negado")
    return db.query(Arquivo).filter(Arquivo.tenant_id == tenant_id).order_by(Arquivo.id.desc()).all()


@router.get("/arquivos/{tenant_id}")
def consultar_arquivos(
    tenant_id: int,
    db: Session = Depends(get_db),
    current_user: Nutricionista = Depends(get_current_user),
):
    return consultar_arquivos_repository(tenant_id, db, current_user)


@router.get("/arquivos/{arquivo_id}/download")
def download_arquivo(
    arquivo_id: int,
    db: Session = Depends(get_db),
    current_user: Nutricionista = Depends(get_current_user),
):
    arquivo = db.query(Arquivo).filter(Arquivo.id == arquivo_id).first()
    if not arquivo:
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    if current_user.papel != "admin" and arquivo.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="Acesso negado")
    return {"caminho_s3": arquivo.caminho_s3}


@router.post("/arquivos/{arquivo_id}/ocr")
def executar_ocr_arquivo(
    arquivo_id: int,
    registrar_no_prontuario: bool = True,
    db: Session = Depends(get_db),
    current_user: Nutricionista = Depends(get_current_user),
):
    arquivo = db.query(Arquivo).filter(Arquivo.id == arquivo_id).first()
    if not arquivo:
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    if current_user.papel != "admin" and arquivo.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="Acesso negado")

    local_path = f"/tmp/{uuid.uuid4()}_{arquivo.nome}"
    if not download_object(arquivo.caminho_s3, local_path):
        raise HTTPException(status_code=500, detail="Falha ao baixar arquivo do Minio")
    try:
        payload = _processar_ocr_arquivo(
            db,
            arquivo=arquivo,
            local_path=local_path,
            current_user=current_user,
            registrar_avanco=registrar_no_prontuario,
        )
    finally:
        if os.path.exists(local_path):
            os.remove(local_path)
    return {
        "arquivo_id": arquivo.id,
        "arquivo_nome": arquivo.nome,
        **payload,
    }
