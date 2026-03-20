from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.domain.models.contabilidade import Contabilidade
from app.db import get_db

router = APIRouter()

@router.post("/contabilidades/criar")
def criar_contabilidade(tipo: str, valor: int, descricao: str, data: str, tenant_id: int = None, cliente_id: int = None, assas_id: str = None, db: Session = Depends(get_db)):
    contabilidade = Contabilidade(
        tipo=tipo,
        valor=valor,
        descricao=descricao,
        data=data,
        tenant_id=tenant_id,
        cliente_id=cliente_id,
        assas_id=assas_id
    )
    db.add(contabilidade)
    db.commit()
    db.refresh(contabilidade)
    return contabilidade

@router.get("/contabilidades/{tenant_id}")
def consultar_contabilidades(tenant_id: int, db: Session = Depends(get_db)):
    contabilidades = db.query(Contabilidade).filter(Contabilidade.tenant_id == tenant_id).all()
    return contabilidades

@router.put("/contabilidades/{contabilidade_id}/atualizar")
def atualizar_contabilidade(contabilidade_id: int, valor: int = None, descricao: str = None, status: str = None, assas_id: str = None, db: Session = Depends(get_db)):
    contabilidade = db.query(Contabilidade).filter(Contabilidade.id == contabilidade_id).first()
    if not contabilidade:
        raise HTTPException(status_code=404, detail="Registro não encontrado")
    if valor:
        contabilidade.valor = valor
    if descricao:
        contabilidade.descricao = descricao
    if status:
        contabilidade.status = status
    if assas_id:
        contabilidade.assas_id = assas_id
    db.commit()
    db.refresh(contabilidade)
    return contabilidade