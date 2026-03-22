from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.api.v1.auth import get_current_user
from app.domain.models.conversa import Conversa
from app.domain.models.nutricionista import Nutricionista
from app.domain.models.relatorio import Relatorio
from app.db import get_db

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

@router.get("/relatorios/tenant/{tenant_id}")
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


@router.get("/relatorios/canais")
def ranking_canais(
    data_inicio: str | None = None,
    data_fim: str | None = None,
    nutricionista_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: Nutricionista = Depends(get_current_user),
):
    query = db.query(
        Conversa.canal_origem,
        func.count(Conversa.id).label("total"),
    ).filter(Conversa.canal_origem.isnot(None))

    if current_user.papel != "admin":
        query = query.filter(Conversa.nutricionista_id == current_user.id)
    elif nutricionista_id:
        query = query.filter(Conversa.nutricionista_id == nutricionista_id)

    if data_inicio:
        query = query.filter(Conversa.data >= datetime.fromisoformat(data_inicio))
    if data_fim:
        query = query.filter(Conversa.data <= datetime.fromisoformat(data_fim))

    rows = query.group_by(Conversa.canal_origem).order_by(func.count(Conversa.id).desc()).all()
    total_global = sum(int(r.total or 0) for r in rows) or 1
    return [
        {
            "canal": r.canal_origem or "desconhecido",
            "total": int(r.total or 0),
            "percentual": round((int(r.total or 0) / total_global) * 100, 2),
        }
        for r in rows
    ]

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
