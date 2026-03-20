from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.domain.models.campanha import Campanha
from app.database import get_db

router = APIRouter()

@router.post("/campanhas/criar")
def criar_campanha(nome: str, descricao: str, tipo: str, tenant_id: int = None, caixa_id: int = None, db: Session = Depends(get_db)):
    campanha = Campanha(
        nome=nome,
        descricao=descricao,
        tipo=tipo,
        tenant_id=tenant_id,
        caixa_id=caixa_id
    )
    db.add(campanha)
    db.commit()
    db.refresh(campanha)
    return campanha

@router.get("/campanhas/{tenant_id}")
def consultar_campanhas(tenant_id: int, db: Session = Depends(get_db)):
    campanhas = db.query(Campanha).filter(Campanha.tenant_id == tenant_id, Campanha.status == "ativa").all()
    return campanhas

@router.put("/campanhas/{campanha_id}/atualizar")
def atualizar_campanha(campanha_id: int, nome: str = None, descricao: str = None, tipo: str = None, status: str = None, db: Session = Depends(get_db)):
    campanha = db.query(Campanha).filter(Campanha.id == campanha_id).first()
    if not campanha:
        raise HTTPException(status_code=404, detail="Campanha não encontrada")
    if nome:
        campanha.nome = nome
    if descricao:
        campanha.descricao = descricao
    if tipo:
        campanha.tipo = tipo
    if status:
        campanha.status = status
    db.commit()
    db.refresh(campanha)
    return campanha

@router.put("/campanhas/{campanha_id}/desativar")
def desativar_campanha(campanha_id: int, db: Session = Depends(get_db)):
    campanha = db.query(Campanha).filter(Campanha.id == campanha_id).first()
    if not campanha:
        raise HTTPException(status_code=404, detail="Campanha não encontrada")
    campanha.status = "inativa"
    db.commit()
    db.refresh(campanha)
    return campanha