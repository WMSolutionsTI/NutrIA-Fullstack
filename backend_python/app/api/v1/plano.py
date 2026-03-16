from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.plano import Plano
from app.database import get_db

router = APIRouter()

@router.post("/planos/criar")
def criar_plano(nome: str, descricao: str, valor: int, limite_caixas: int, tenant_id: int = None, db: Session = Depends(get_db)):
    plano = Plano(
        nome=nome,
        descricao=descricao,
        valor=valor,
        limite_caixas=limite_caixas,
        tenant_id=tenant_id
    )
    db.add(plano)
    db.commit()
    db.refresh(plano)
    return plano

@router.get("/planos/{tenant_id}")
def consultar_planos(tenant_id: int, db: Session = Depends(get_db)):
    planos = db.query(Plano).filter(Plano.tenant_id == tenant_id, Plano.ativo == 1).all()
    return planos

@router.put("/planos/{plano_id}/atualizar")
def atualizar_plano(plano_id: int, nome: str = None, descricao: str = None, valor: int = None, limite_caixas: int = None, db: Session = Depends(get_db)):
    plano = db.query(Plano).filter(Plano.id == plano_id).first()
    if not plano:
        raise HTTPException(status_code=404, detail="Plano não encontrado")
    if nome:
        plano.nome = nome
    if descricao:
        plano.descricao = descricao
    if valor:
        plano.valor = valor
    if limite_caixas:
        plano.limite_caixas = limite_caixas
    db.commit()
    db.refresh(plano)
    return plano

@router.put("/planos/{plano_id}/desativar")
def desativar_plano(plano_id: int, db: Session = Depends(get_db)):
    plano = db.query(Plano).filter(Plano.id == plano_id).first()
    if not plano:
        raise HTTPException(status_code=404, detail="Plano não encontrado")
    plano.ativo = 0
    db.commit()
    db.refresh(plano)
    return plano

@router.post("/planos/{plano_id}/upgrade")
def upgrade_plano(plano_id: int, novo_limite: int, db: Session = Depends(get_db)):
    plano = db.query(Plano).filter(Plano.id == plano_id).first()
    if not plano:
        raise HTTPException(status_code=404, detail="Plano não encontrado")
    plano.limite_caixas = novo_limite
    db.commit()
    db.refresh(plano)
    return plano

@router.post("/planos/{plano_id}/downgrade")
def downgrade_plano(plano_id: int, novo_limite: int, db: Session = Depends(get_db)):
    plano = db.query(Plano).filter(Plano.id == plano_id).first()
    if not plano:
        raise HTTPException(status_code=404, detail="Plano não encontrado")
    plano.limite_caixas = novo_limite
    db.commit()
    db.refresh(plano)
    return plano

@router.get("/planos/{plano_id}/permissoes")
def consultar_permissoes(plano_id: int, db: Session = Depends(get_db)):
    plano = db.query(Plano).filter(Plano.id == plano_id).first()
    if not plano:
        raise HTTPException(status_code=404, detail="Plano não encontrado")
    # Mock: permissões
    return {"plano_id": plano.id, "permissoes": ["nutricionista", "admin", "relatorio"]}