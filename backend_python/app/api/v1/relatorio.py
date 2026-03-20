from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.domain.models.relatorio import Relatorio
from app.database import get_db

router = APIRouter()

@router.post("/relatorios/criar")
def criar_relatorio(tipo: str, descricao: str, data_inicio: str, data_fim: str, arquivo: str = None, tenant_id: int = None, caixa_id: int = None, db: Session = Depends(get_db)):
    relatorio = Relatorio(
        tipo=tipo,
        descricao=descricao,
        data_inicio=data_inicio,
        data_fim=data_fim,
        arquivo=arquivo,
        tenant_id=tenant_id,
        caixa_id=caixa_id
    )
    db.add(relatorio)
    db.commit()
    db.refresh(relatorio)
    return relatorio

@router.get("/relatorios/{tenant_id}")
def consultar_relatorios(tenant_id: int, db: Session = Depends(get_db)):
    relatorios = db.query(Relatorio).filter(Relatorio.tenant_id == tenant_id).all()
    return relatorios

@router.get("/relatorios/{relatorio_id}/download")
def download_relatorio(relatorio_id: int, db: Session = Depends(get_db)):
    relatorio = db.query(Relatorio).filter(Relatorio.id == relatorio_id).first()
    if not relatorio or not relatorio.arquivo:
        raise HTTPException(status_code=404, detail="Relatório ou arquivo não encontrado")
    # Aqui seria implementada a lógica de download/exportação
    return {"arquivo": relatorio.arquivo}

@router.put("/relatorios/{relatorio_id}/atualizar")
def atualizar_relatorio(relatorio_id: int, descricao: str = None, arquivo: str = None, db: Session = Depends(get_db)):
    relatorio = db.query(Relatorio).filter(Relatorio.id == relatorio_id).first()
    if not relatorio:
        raise HTTPException(status_code=404, detail="Relatório não encontrado")
    if descricao:
        relatorio.descricao = descricao
    if arquivo:
        relatorio.arquivo = arquivo
    db.commit()
    db.refresh(relatorio)
    return relatorio