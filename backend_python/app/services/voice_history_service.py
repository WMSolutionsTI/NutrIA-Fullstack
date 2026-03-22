from datetime import datetime
import os
import tempfile
import uuid

import requests
from sqlalchemy.orm import Session

from app.domain.models.arquivo import Arquivo
from app.domain.models.conversa import Conversa
from app.workers.minio_worker import upload_object


def _latest_conversa_id(db: Session, cliente_id: int | None, nutricionista_id: int) -> int | None:
    if not cliente_id:
        return None
    conversa = (
        db.query(Conversa)
        .filter(Conversa.cliente_id == cliente_id, Conversa.nutricionista_id == nutricionista_id)
        .order_by(Conversa.id.desc())
        .first()
    )
    return conversa.id if conversa else None


def persist_audio_from_local_file(
    db: Session,
    *,
    tenant_id: int,
    nutricionista_id: int,
    cliente_id: int | None,
    local_path: str,
    original_filename: str | None = None,
    nota_conversa: str | None = None,
) -> dict | None:
    if not os.path.exists(local_path):
        return None
    file_name = original_filename or os.path.basename(local_path)
    object_name = (
        f"{tenant_id}/voice/{nutricionista_id}/{cliente_id or 'sem-cliente'}/"
        f"{uuid.uuid4().hex}_{file_name}"
    )
    if not upload_object(object_name, local_path):
        return None

    conversa_id = _latest_conversa_id(db, cliente_id, nutricionista_id)
    arquivo = Arquivo(
        nome=file_name,
        tipo="audio",
        caminho_s3=object_name,
        tamanho=os.path.getsize(local_path),
        criado_em=datetime.utcnow(),
        tenant_id=tenant_id,
        cliente_id=cliente_id,
        conversa_id=conversa_id,
    )
    db.add(arquivo)
    db.commit()
    db.refresh(arquivo)

    if cliente_id and nota_conversa:
        conversa = Conversa(
            cliente_id=cliente_id,
            nutricionista_id=nutricionista_id,
            caixa_id=None,
            mensagem=f"{nota_conversa} [arquivo_id={arquivo.id}]",
            modo="ia",
            em_conversa_direta=False,
            data=datetime.utcnow(),
        )
        db.add(conversa)
        db.commit()

    return {"arquivo_id": arquivo.id, "caminho_s3": object_name}


def persist_audio_from_url(
    db: Session,
    *,
    tenant_id: int,
    nutricionista_id: int,
    cliente_id: int | None,
    remote_url: str,
    filename_hint: str,
    nota_conversa: str | None = None,
) -> dict | None:
    if not remote_url:
        return None
    local_path = None
    try:
        response = requests.get(remote_url, timeout=30)
        response.raise_for_status()
        fd, local_path = tempfile.mkstemp(suffix=".mp3", prefix="voice-recording-")
        with os.fdopen(fd, "wb") as f:
            f.write(response.content)
        return persist_audio_from_local_file(
            db,
            tenant_id=tenant_id,
            nutricionista_id=nutricionista_id,
            cliente_id=cliente_id,
            local_path=local_path,
            original_filename=filename_hint,
            nota_conversa=nota_conversa,
        )
    except Exception:
        return None
    finally:
        if local_path and os.path.exists(local_path):
            try:
                os.remove(local_path)
            except Exception:
                pass

