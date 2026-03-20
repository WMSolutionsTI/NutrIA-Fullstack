from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.domain.models.relatorio import Relatorio
from app.db import get_db

router = APIRouter()

@router.get("/analytics/dashboard")
def dashboard_analytics(tenant_id: int, db: Session = Depends(get_db)):
    # Mock: sumarização de relatórios
    relatorios = db.query(Relatorio).filter(Relatorio.tenant_id == tenant_id).all()
    total_relatorios = len(relatorios)
    tipos = {}
    for r in relatorios:
        tipos[r.tipo] = tipos.get(r.tipo, 0) + 1
    return {"total_relatorios": total_relatorios, "tipos": tipos}