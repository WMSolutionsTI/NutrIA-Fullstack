from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.domain.models.cliente import Cliente
from app.db import get_db

router = APIRouter()

@router.get("/plano_alimentar/{cliente_id}")
def consultar_plano_alimentar(cliente_id: int, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    # Mock: plano alimentar
    return {"cliente_id": cliente.id, "plano_alimentar": "Plano alimentar atual"}

@router.post("/plano_alimentar/{cliente_id}/gerar_ia")
def gerar_plano_ia(cliente_id: int, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    # Mock: geração IA
    return {"cliente_id": cliente.id, "plano_ia": "Plano alimentar gerado por IA"}

@router.put("/plano_alimentar/{cliente_id}/editar")
def editar_plano_alimentar(cliente_id: int, novo_plano: str, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    # Mock: edição
    return {"cliente_id": cliente.id, "plano_alimentar": novo_plano}

@router.get("/plano_alimentar/{cliente_id}/historico")
def historico_plano_alimentar(cliente_id: int, db: Session = Depends(get_db)):
    # Mock: histórico
    return {"cliente_id": cliente_id, "historico": ["Plano 1", "Plano 2"]}