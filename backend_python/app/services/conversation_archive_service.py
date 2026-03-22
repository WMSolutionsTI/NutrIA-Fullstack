from datetime import datetime
import json
import os
import tempfile
import uuid

from sqlalchemy.orm import Session

from app.domain.models.arquivo import Arquivo
from app.domain.models.conversa import Conversa
from app.workers.minio_worker import upload_object


def archive_conversa_snapshot(
    db: Session,
    *,
    conversa: Conversa,
    tenant_id: int | None,
) -> dict | None:
    if not tenant_id:
        return None
    if not conversa:
        return None

    payload = {
        "conversa_id": conversa.id,
        "cliente_id": conversa.cliente_id,
        "nutricionista_id": conversa.nutricionista_id,
        "caixa_id": conversa.caixa_id,
        "chatwoot_account_id": conversa.chatwoot_account_id,
        "chatwoot_inbox_id": conversa.chatwoot_inbox_id,
        "canal_origem": conversa.canal_origem,
        "chatwoot_conversation_id": conversa.chatwoot_conversation_id,
        "mensagem": conversa.mensagem,
        "modo": conversa.modo,
        "em_conversa_direta": bool(conversa.em_conversa_direta),
        "contexto_ia": conversa.contexto_ia,
        "data": (conversa.data.isoformat() if conversa.data else None),
        "archived_at": datetime.utcnow().isoformat(),
    }
    fd, local_path = tempfile.mkstemp(suffix=".json", prefix="conversa-archive-")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False)

        object_name = f"{tenant_id}/conversas/{conversa.nutricionista_id}/{conversa.id}_{uuid.uuid4().hex}.json"
        if not upload_object(object_name, local_path):
            return None

        arquivo = Arquivo(
            nome=f"conversa_{conversa.id}.json",
            tipo="documento",
            caminho_s3=object_name,
            tamanho=os.path.getsize(local_path),
            criado_em=datetime.utcnow(),
            tenant_id=tenant_id,
            cliente_id=conversa.cliente_id,
            conversa_id=conversa.id,
        )
        db.add(arquivo)
        db.commit()
        db.refresh(arquivo)
        return {"arquivo_id": arquivo.id, "caminho_s3": object_name}
    finally:
        if os.path.exists(local_path):
            try:
                os.remove(local_path)
            except Exception:
                pass
