from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.domain.models.contabilidade import Contabilidade
from app.domain.models.cliente import Cliente
from app.domain.models.relatorio import Relatorio
from app.domain.models.nutricionista import Nutricionista
from app.database import get_db

router = APIRouter(prefix="/suporte_nutri", tags=["Suporte Nutricionista"])

@router.get("/painel")
def painel_nutri(nutri_id: int, db: Session = Depends(get_db)):
    nutri = db.query(Nutricionista).filter(Nutricionista.id == nutri_id).first()
    if not nutri:
        raise HTTPException(status_code=404, detail="Nutricionista não encontrado")
    tenant_id = nutri.tenant_id

    # Estatísticas financeiras
    receitas = db.query(Contabilidade).filter(Contabilidade.tenant_id == tenant_id, Contabilidade.tipo == "receita").all()
    despesas = db.query(Contabilidade).filter(Contabilidade.tenant_id == tenant_id, Contabilidade.tipo == "despesa").all()
    total_receitas = sum(r.valor for r in receitas)
    total_despesas = sum(d.valor for d in despesas)
    saldo = total_receitas - total_despesas

    # Estatísticas de clientes
    clientes = db.query(Cliente).filter(Cliente.nutricionista_id == nutri_id).all()
    total_clientes = len(clientes)

    # Estatísticas de relatórios
    relatorios = db.query(Relatorio).filter(Relatorio.tenant_id == tenant_id).all()
    total_relatorios = len(relatorios)

    return {
        "nutricionista_id": nutri_id,
        "tenant_id": tenant_id,
        "financeiro": {
            "total_receitas": total_receitas,
            "total_despesas": total_despesas,
            "saldo": saldo
        },
        "clientes": {
            "total_clientes": total_clientes
        },
        "relatorios": {
            "total_relatorios": total_relatorios
        }
    }
