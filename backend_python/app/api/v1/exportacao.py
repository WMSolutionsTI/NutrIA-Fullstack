from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.domain.models.relatorio import Relatorio
from app.database import get_db

router = APIRouter()

@router.post("/exportacao/relatorio")
def exportar_relatorio(relatorio_id: int, db: Session = Depends(get_db)):
    relatorio = db.query(Relatorio).filter(Relatorio.id == relatorio_id).first()
    if not relatorio or not relatorio.arquivo:
        raise HTTPException(status_code=404, detail="Relatório ou arquivo não encontrado")
    # Mock: exportação
    return {"arquivo": relatorio.arquivo, "status": "exportado"}