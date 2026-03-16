from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.tenant import Tenant
from app.database import get_db

router = APIRouter()

@router.get("/tenant/{tenant_id}")
def consultar_tenant(tenant_id: int, db: Session = Depends(get_db)):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant não encontrado")
    return tenant

@router.get("/tenant/{tenant_id}/isolamento")
def verificar_isolamento(tenant_id: int, db: Session = Depends(get_db)):
    # Mock: verificação de isolamento
    return {"tenant_id": tenant_id, "isolamento": True}