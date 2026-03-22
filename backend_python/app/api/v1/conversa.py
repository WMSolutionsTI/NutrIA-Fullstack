from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.v1.auth import get_current_user
from app.db import get_db
from app.domain.models.cliente import Cliente
from app.domain.models.conversa import Conversa
from app.domain.models.nutricionista import Nutricionista
from app.services.conversation_archive_service import archive_conversa_snapshot

router = APIRouter(prefix="/conversas", tags=["Conversas"])


def _get_conversa_or_404(db: Session, conversa_id: int) -> Conversa:
    conversa = db.query(Conversa).filter(Conversa.id == conversa_id).first()
    if not conversa:
        raise HTTPException(status_code=404, detail="Conversa não encontrada")
    return conversa


def _resolve_nutricionista_owner_id(db: Session, conversa: Conversa) -> int | None:
    if conversa.nutricionista_id:
        return conversa.nutricionista_id
    if conversa.cliente_id:
        cliente = db.query(Cliente).filter(Cliente.id == conversa.cliente_id).first()
        if cliente:
            return cliente.nutricionista_id
    return None


def _ensure_can_access_nutricionista(
    db: Session, target_nutricionista_id: int | None, current_user: Nutricionista
) -> None:
    if current_user.papel == "admin":
        return

    if target_nutricionista_id == current_user.id:
        return

    if current_user.tenant_id and target_nutricionista_id:
        target_nutri = db.query(Nutricionista).filter(Nutricionista.id == target_nutricionista_id).first()
        if target_nutri and target_nutri.tenant_id == current_user.tenant_id:
            return

    raise HTTPException(status_code=403, detail="Acesso negado")


def _ensure_can_access_conversa(
    db: Session, conversa: Conversa, current_user: Nutricionista
) -> None:
    owner_nutri_id = _resolve_nutricionista_owner_id(db, conversa)
    _ensure_can_access_nutricionista(db, owner_nutri_id, current_user)


def _tenant_id_from_nutri(db: Session, nutricionista_id: int | None) -> int | None:
    if not nutricionista_id:
        return None
    nutri = db.query(Nutricionista).filter(Nutricionista.id == nutricionista_id).first()
    return nutri.tenant_id if nutri else None


@router.post("/", response_model=dict)
def create_conversa(
    conversa: dict,
    db: Session = Depends(get_db),
    current_user: Nutricionista = Depends(get_current_user),
):
    payload = conversa.copy()

    cliente_id = payload.get("cliente_id")
    cliente = None
    if cliente_id:
        cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")

    owner_nutri_id = payload.get("nutricionista_id") or (cliente.nutricionista_id if cliente else None)
    _ensure_can_access_nutricionista(db, owner_nutri_id, current_user)

    if current_user.papel != "admin":
        payload["nutricionista_id"] = owner_nutri_id or current_user.id

    new_conversa = Conversa(**payload)
    db.add(new_conversa)
    db.commit()
    db.refresh(new_conversa)
    tenant_id = _tenant_id_from_nutri(db, new_conversa.nutricionista_id)
    archive_conversa_snapshot(db, conversa=new_conversa, tenant_id=tenant_id)
    return {"id": new_conversa.id}

@router.get("/cliente/{cliente_id}", response_model=list)
def get_conversas_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    current_user: Nutricionista = Depends(get_current_user),
):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    _ensure_can_access_nutricionista(db, cliente.nutricionista_id, current_user)
    return db.query(Conversa).filter_by(cliente_id=cliente_id).all()

@router.get("/nutricionista/{nutricionista_id}", response_model=list)
def get_conversas_nutricionista(
    nutricionista_id: int,
    db: Session = Depends(get_db),
    current_user: Nutricionista = Depends(get_current_user),
):
    _ensure_can_access_nutricionista(db, nutricionista_id, current_user)
    return db.query(Conversa).filter_by(nutricionista_id=nutricionista_id).all()

@router.get("/{conversa_id}", response_model=dict)
def get_conversa(
    conversa_id: int,
    db: Session = Depends(get_db),
    current_user: Nutricionista = Depends(get_current_user),
):
    conversa = _get_conversa_or_404(db, conversa_id)
    _ensure_can_access_conversa(db, conversa, current_user)
    return conversa.__dict__

@router.post("/conversas/{conversa_id}/modo")
def alternar_modo_conversa(
    conversa_id: int,
    modo: str,
    db: Session = Depends(get_db),
    current_user: Nutricionista = Depends(get_current_user),
):
    conversa = _get_conversa_or_404(db, conversa_id)
    _ensure_can_access_conversa(db, conversa, current_user)
    if modo not in ["ia", "direto"]:
        raise HTTPException(status_code=400, detail="Modo inválido")
    conversa.modo = modo
    conversa.em_conversa_direta = (modo == "direto")
    if conversa.cliente_id:
        cliente = conversa.cliente
        if cliente:
            cliente.status = "em_atendimento_direto" if modo == "direto" else "cliente_ativo"
            db.add(cliente)
    db.commit()
    db.refresh(conversa)
    return {"id": conversa.id, "modo": conversa.modo, "em_conversa_direta": conversa.em_conversa_direta}

@router.post("/conversas/{conversa_id}/abrir")
def abrir_conversa_direta(
    conversa_id: int,
    db: Session = Depends(get_db),
    current_user: Nutricionista = Depends(get_current_user),
):
    conversa = _get_conversa_or_404(db, conversa_id)
    _ensure_can_access_conversa(db, conversa, current_user)
    conversa.modo = "direto"
    conversa.em_conversa_direta = True
    if conversa.cliente_id:
        cliente = conversa.cliente
        if cliente:
            cliente.status = "em_atendimento_direto"
            db.add(cliente)
    db.add(conversa)
    db.commit()
    db.refresh(conversa)
    return {"id": conversa.id, "modo": conversa.modo, "em_conversa_direta": conversa.em_conversa_direta}

@router.post("/conversas/{conversa_id}/fechar")
def fechar_conversa_direta(
    conversa_id: int,
    db: Session = Depends(get_db),
    current_user: Nutricionista = Depends(get_current_user),
):
    conversa = _get_conversa_or_404(db, conversa_id)
    _ensure_can_access_conversa(db, conversa, current_user)
    conversa.modo = "ia"
    conversa.em_conversa_direta = False
    if conversa.cliente_id:
        cliente = conversa.cliente
        if cliente:
            cliente.status = "cliente_ativo"
            db.add(cliente)
    db.add(conversa)
    db.commit()
    db.refresh(conversa)
    return {"id": conversa.id, "modo": conversa.modo, "em_conversa_direta": conversa.em_conversa_direta}

@router.get("/conversas/{conversa_id}/status")
def status_conversa(
    conversa_id: int,
    db: Session = Depends(get_db),
    current_user: Nutricionista = Depends(get_current_user),
):
    conversa = _get_conversa_or_404(db, conversa_id)
    _ensure_can_access_conversa(db, conversa, current_user)
    return {"id": conversa.id, "modo": conversa.modo, "em_conversa_direta": conversa.em_conversa_direta}

@router.post("/conversas/armazenar")
def armazenar_conversa(
    cliente_id: int,
    nutricionista_id: int,
    caixa_id: int,
    mensagem: str,
    modo: str = "ia",
    contexto_ia: str = None,
    db: Session = Depends(get_db),
    current_user: Nutricionista = Depends(get_current_user),
):
    _ensure_can_access_nutricionista(db, nutricionista_id, current_user)
    conversa = Conversa(
        cliente_id=cliente_id,
        nutricionista_id=nutricionista_id,
        caixa_id=caixa_id,
        mensagem=mensagem,
        modo=modo,
        contexto_ia=contexto_ia,
        em_conversa_direta=(modo=="direto")
    )
    db.add(conversa)
    db.commit()
    db.refresh(conversa)
    tenant_id = _tenant_id_from_nutri(db, conversa.nutricionista_id)
    archive_conversa_snapshot(db, conversa=conversa, tenant_id=tenant_id)
    return conversa
