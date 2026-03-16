from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.relatorio import Relatorio
from app.database import get_db

router = APIRouter()

@router.get("/logs/relatorios")
def logs_relatorios(tenant_id: int, db: Session = Depends(get_db)):
    relatorios = db.query(Relatorio).filter(Relatorio.tenant_id == tenant_id).all()
    # Mock: logs
    return [{"id": r.id, "tipo": r.tipo, "arquivo": r.arquivo} for r in relatorios]