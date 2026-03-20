from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.domain.models.conversa import Conversa
from app.db import get_db

router = APIRouter(prefix="/conversas", tags=["Conversas"])

@router.post("/", response_model=dict)
def create_conversa(conversa: dict, db: Session = Depends(get_db)):
    new_conversa = Conversa(**conversa)
    db.add(new_conversa)
    db.commit()
    db.refresh(new_conversa)
    return {"id": new_conversa.id}

@router.get("/cliente/{cliente_id}", response_model=list)
def get_conversas_cliente(cliente_id: int, db: Session = Depends(get_db)):
    return db.query(Conversa).filter_by(cliente_id=cliente_id).all()

@router.get("/nutricionista/{nutricionista_id}", response_model=list)
def get_conversas_nutricionista(nutricionista_id: int, db: Session = Depends(get_db)):
    return db.query(Conversa).filter_by(nutricionista_id=nutricionista_id).all()

@router.get("/{conversa_id}", response_model=dict)
def get_conversa(conversa_id: int, db: Session = Depends(get_db)):
    conversa = db.query(Conversa).get(conversa_id)
    if not conversa:
        raise HTTPException(status_code=404, detail="Conversa não encontrada")
    return conversa.__dict__

@router.post("/conversas/{conversa_id}/modo")
def alternar_modo_conversa(conversa_id: int, modo: str, db: Session = Depends(get_db)):
    conversa = db.query(Conversa).filter(Conversa.id == conversa_id).first()
    if not conversa:
        raise HTTPException(status_code=404, detail="Conversa não encontrada")
    if modo not in ["ia", "direto"]:
        raise HTTPException(status_code=400, detail="Modo inválido")
    conversa.modo = modo
    conversa.em_conversa_direta = (modo == "direto")
    db.commit()
    db.refresh(conversa)
    return {"id": conversa.id, "modo": conversa.modo, "em_conversa_direta": conversa.em_conversa_direta}

@router.get("/conversas/{conversa_id}/status")
def status_conversa(conversa_id: int, db: Session = Depends(get_db)):
    conversa = db.query(Conversa).filter(Conversa.id == conversa_id).first()
    if not conversa:
        raise HTTPException(status_code=404, detail="Conversa não encontrada")
    return {"id": conversa.id, "modo": conversa.modo, "em_conversa_direta": conversa.em_conversa_direta}

@router.post("/conversas/armazenar")
def armazenar_conversa(cliente_id: int, nutricionista_id: int, caixa_id: int, mensagem: str, modo: str = "ia", contexto_ia: str = None, db: Session = Depends(get_db)):
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
    return conversa