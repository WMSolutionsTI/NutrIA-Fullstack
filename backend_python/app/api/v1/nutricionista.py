from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from shared.models.nutricionista import Nutricionista
from shared.models.tenant import Tenant
from shared.models.caixa_de_entrada import CaixaDeEntrada
from app.db import get_db

router = APIRouter(prefix="/nutricionistas", tags=["Nutricionistas"])

@router.get("/", response_model=list)
def list_nutricionistas(db: Session = Depends(get_db)):
    return db.query(Nutricionista).all()

@router.post("/", response_model=dict)
def create_nutricionista(nutri: dict, db: Session = Depends(get_db)):
    new_nutri = Nutricionista(**nutri)
    db.add(new_nutri)
    db.commit()
    db.refresh(new_nutri)
    return {"id": new_nutri.id}

@router.get("/{nutri_id}", response_model=dict)
def get_nutricionista(nutri_id: int, tenant_id: int, db: Session = Depends(get_db)):
    nutri = db.query(Nutricionista).filter(Nutricionista.id == nutri_id, Nutricionista.tenant_id == tenant_id).first()
    if not nutri:
        raise HTTPException(status_code=404, detail="Nutricionista não encontrado ou tenant inválido")
    return nutri.__dict__

@router.put("/{nutri_id}", response_model=dict)
def update_nutricionista(nutri_id: int, tenant_id: int, nutri_data: dict, db: Session = Depends(get_db)):
    nutri = db.query(Nutricionista).filter(Nutricionista.id == nutri_id, Nutricionista.tenant_id == tenant_id).first()
    if not nutri:
        raise HTTPException(status_code=404, detail="Nutricionista não encontrado ou tenant inválido")
    for k, v in nutri_data.items():
        setattr(nutri, k, v)
    db.commit()
    db.refresh(nutri)
    return nutri.__dict__

@router.delete("/{nutri_id}", response_model=dict)
def delete_nutricionista(nutri_id: int, tenant_id: int, db: Session = Depends(get_db)):
    nutri = db.query(Nutricionista).filter(Nutricionista.id == nutri_id, Nutricionista.tenant_id == tenant_id).first()
    if not nutri:
        raise HTTPException(status_code=404, detail="Nutricionista não encontrado ou tenant inválido")
    db.delete(nutri)
    db.commit()
    return {"status": "deleted"}