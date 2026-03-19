from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.contabilidade import Contabilidade
from app.models.cliente import Cliente
from app.models.relatorio import Relatorio
from app.models.nutricionista import Nutricionista
from app.database import get_db

router = APIRouter(prefix="/estatisticas", tags=["Estatísticas Nutricionista"])

# Dependência para garantir que o usuário autenticado é um nutricionista do tenant
# (Aqui é um mock, ajuste para seu sistema de autenticação real)
def get_current_nutricionista(db: Session = Depends(get_db), nutricionista_id: int = None, tenant_id: int = None):
    nutri = db.query(Nutricionista).filter(Nutricionista.id == nutricionista_id, Nutricionista.tenant_id == tenant_id).first()
    if not nutri:
        raise HTTPException(status_code=403, detail="Acesso restrito ao nutricionista do tenant")
    return nutri

@router.get("/financeiro")
def estatisticas_financeiro(nutricionista: Nutricionista = Depends(get_current_nutricionista), db: Session = Depends(get_db)):
    tenant_id = nutricionista.tenant_id
    receitas = db.query(Contabilidade).filter(Contabilidade.tenant_id == tenant_id, Contabilidade.tipo == "receita").all()
    despesas = db.query(Contabilidade).filter(Contabilidade.tenant_id == tenant_id, Contabilidade.tipo == "despesa").all()
    total_receitas = sum(r.valor for r in receitas)
    total_despesas = sum(d.valor for d in despesas)
    saldo = total_receitas - total_despesas
    return {
        "total_receitas": total_receitas,
        "total_despesas": total_despesas,
        "saldo": saldo,
        "qtd_lancamentos": len(receitas) + len(despesas)
    }

@router.get("/clientes")
def estatisticas_clientes(nutricionista: Nutricionista = Depends(get_current_nutricionista), db: Session = Depends(get_db)):
    tenant_id = nutricionista.tenant_id
    total_clientes = db.query(Cliente).filter(Cliente.nutricionista_id == nutricionista.id).count()
    return {
        "total_clientes": total_clientes
    }

@router.get("/relatorios")
def estatisticas_relatorios(nutricionista: Nutricionista = Depends(get_current_nutricionista), db: Session = Depends(get_db)):
    tenant_id = nutricionista.tenant_id
    relatorios = db.query(Relatorio).filter(Relatorio.tenant_id == tenant_id).all()
    total_relatorios = len(relatorios)
    tipos = {}
    for r in relatorios:
        tipos[r.tipo] = tipos.get(r.tipo, 0) + 1
    return {
        "total_relatorios": total_relatorios,
        "tipos": tipos
    }
