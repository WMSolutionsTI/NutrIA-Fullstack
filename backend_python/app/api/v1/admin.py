from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.domain.models.nutricionista import Nutricionista
from app.domain.models.cliente import Cliente
from app.domain.models.caixa_de_entrada import CaixaDeEntrada
from app.domain.models.plano import Plano
from app.domain.models.campanha import Campanha
from app.domain.models.relatorio import Relatorio
from app.domain.models.contabilidade import Contabilidade
from app.domain.models.arquivo import Arquivo
from app.db import get_db

router = APIRouter()

# Endpoints de gestão de nutricionistas
@router.get("/admin/nutricionistas")
def listar_nutricionistas(db: Session = Depends(get_db)):
    return db.query(Nutricionista).all()

@router.post("/admin/nutricionistas/criar")
def criar_nutricionista(nome: str, email: str, tenant_id: int, db: Session = Depends(get_db)):
    nutricionista = Nutricionista(nome=nome, email=email, tenant_id=tenant_id)
    db.add(nutricionista)
    db.commit()
    db.refresh(nutricionista)
    return nutricionista

# Endpoints de gestão de clientes
@router.get("/admin/clientes")
def listar_clientes(db: Session = Depends(get_db)):
    return db.query(Cliente).all()

# Endpoints de gestão de caixas de entrada
@router.get("/admin/caixas")
def listar_caixas(db: Session = Depends(get_db)):
    return db.query(CaixaDeEntrada).all()

# Endpoints de gestão de planos
@router.get("/admin/planos")
def listar_planos(db: Session = Depends(get_db)):
    return db.query(Plano).all()

# Endpoints de gestão de campanhas
@router.get("/admin/campanhas")
def listar_campanhas(db: Session = Depends(get_db)):
    return db.query(Campanha).all()

# Endpoints de gestão de relatórios
@router.get("/admin/relatorios")
def listar_relatorios(db: Session = Depends(get_db)):
    return db.query(Relatorio).all()

# Endpoints de gestão de contabilidade
@router.get("/admin/contabilidade")
def listar_contabilidade(db: Session = Depends(get_db)):
    return db.query(Contabilidade).all()

# Endpoints de gestão de arquivos
@router.get("/admin/arquivos")
def listar_arquivos(db: Session = Depends(get_db)):
    return db.query(Arquivo).all()