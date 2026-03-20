from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.domain.models.caixa_de_entrada import CaixaDeEntrada
from app.domain.models.nutricionista import Nutricionista
from app.domain.models.tenant import Tenant
from app.db import get_db

router = APIRouter(prefix="/caixas", tags=["Caixas de Entrada"])

@router.get("/", response_model=list)
def list_caixas(db: Session = Depends(get_db)):
    return db.query(CaixaDeEntrada).all()

@router.post("/", response_model=dict)
def create_caixa(caixa: dict, db: Session = Depends(get_db)):
    new_caixa = CaixaDeEntrada(**caixa)
    db.add(new_caixa)
    db.commit()
    db.refresh(new_caixa)
    return {"id": new_caixa.id}

@router.get("/{caixa_id}", response_model=dict)
def get_caixa(caixa_id: int, db: Session = Depends(get_db)):
    caixa = db.query(CaixaDeEntrada).get(caixa_id)
    if not caixa:
        raise HTTPException(status_code=404, detail="Caixa não encontrada")
    return caixa.__dict__

@router.put("/{caixa_id}", response_model=dict)
def update_caixa(caixa_id: int, caixa_data: dict, db: Session = Depends(get_db)):
    caixa = db.query(CaixaDeEntrada).get(caixa_id)
    if not caixa:
        raise HTTPException(status_code=404, detail="Caixa não encontrada")
    for k, v in caixa_data.items():
        setattr(caixa, k, v)
    db.commit()
    db.refresh(caixa)
    return caixa.__dict__

@router.delete("/{caixa_id}", response_model=dict)
def delete_caixa(caixa_id: int, db: Session = Depends(get_db)):
    caixa = db.query(CaixaDeEntrada).get(caixa_id)
    if not caixa:
        raise HTTPException(status_code=404, detail="Caixa não encontrada")
    db.delete(caixa)
    db.commit()
    return {"status": "deleted"}

@router.post("/acquire", response_model=dict)
def acquire_caixa(nutricionista_id: int, tipo: str, identificador_chatwoot: str, db: Session = Depends(get_db)):
    nutri = db.query(Nutricionista).get(nutricionista_id)
    if not nutri:
        raise HTTPException(status_code=404, detail="Nutricionista não encontrado")
    tenant = db.query(Tenant).get(nutri.tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant não encontrado")
    # Verifica limite de caixas pelo plano
    limite = int(tenant.limites or "5")  # Exemplo: default 5
    if len(nutri.caixas_de_entrada) >= limite:
        raise HTTPException(status_code=403, detail="Limite de caixas atingido para o plano atual")
    new_caixa = CaixaDeEntrada(
        tipo=tipo,
        identificador_chatwoot=identificador_chatwoot,
        nutricionista_id=nutricionista_id,
        status="active"
    )
    db.add(new_caixa)
    db.commit()
    db.refresh(new_caixa)
    return {"id": new_caixa.id, "status": "acquired"}

@router.post("/upgrade", response_model=dict)
def upgrade_caixa(caixa_id: int, db: Session = Depends(get_db)):
    caixa = db.query(CaixaDeEntrada).get(caixa_id)
    if not caixa:
        raise HTTPException(status_code=404, detail="Caixa não encontrada")
    caixa.status = "upgraded"
    db.commit()
    db.refresh(caixa)
    return {"id": caixa.id, "status": "upgraded"}