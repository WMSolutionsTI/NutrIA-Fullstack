from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.domain.models.cliente import Cliente
from app.domain.models.arquivo import Arquivo
from app.domain.models.conversa import Conversa
from app.domain.models.exame import Exame
from app.domain.models.plano_alimentar import PlanoAlimentar
from app.domain.models.pagamento import Pagamento
from app.domain.models.objetivo import Objetivo
from app.domain.models.avanco import Avanco
from app.db import get_db

router = APIRouter()

@router.get("/prontuario/{cliente_id}")
def consultar_prontuario(cliente_id: int, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return {"id": cliente.id, "nome": cliente.nome, "historico": cliente.historico}

@router.post("/prontuario/{cliente_id}/anexo")
def anexar_documento(cliente_id: int, arquivo_id: int, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    arquivo = db.query(Arquivo).filter(Arquivo.id == arquivo_id).first()
    if not cliente or not arquivo:
        raise HTTPException(status_code=404, detail="Cliente ou arquivo não encontrado")
    # Mock: vincular arquivo ao histórico
    return {"status": "anexado", "cliente_id": cliente.id, "arquivo_id": arquivo.id}

@router.post("/prontuario/{cliente_id}/ia")
def gerar_resumo_ia(cliente_id: int, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    # Mock: geração IA
    return {"cliente_id": cliente.id, "resumo_ia": "Resumo gerado por IA"}


# --> exames
@router.post("/prontuario/{cliente_id}/exames")
def criar_exame(cliente_id: int, exame: dict, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    novo = Exame(cliente_id=cliente_id, nutricionista_id=cliente.nutricionista_id or 0, **exame)
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo


@router.get("/prontuario/{cliente_id}/exames")
def listar_exames(cliente_id: int, db: Session = Depends(get_db)):
    return db.query(Exame).filter(Exame.cliente_id == cliente_id).all()


# --> planos alimentares
@router.post("/prontuario/{cliente_id}/planos")
def criar_plano(cliente_id: int, plano: dict, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    novo = PlanoAlimentar(cliente_id=cliente_id, nutricionista_id=cliente.nutricionista_id or 0, **plano)
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo


@router.get("/prontuario/{cliente_id}/planos")
def listar_planos(cliente_id: int, db: Session = Depends(get_db)):
    return db.query(PlanoAlimentar).filter(PlanoAlimentar.cliente_id == cliente_id).all()


# --> pagamentos
@router.post("/prontuario/{cliente_id}/pagamentos")
def criar_pagamento(cliente_id: int, pagamento: dict, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    novo = Pagamento(cliente_id=cliente_id, nutricionista_id=cliente.nutricionista_id or 0, **pagamento)
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo


@router.get("/prontuario/{cliente_id}/pagamentos")
def listar_pagamentos(cliente_id: int, db: Session = Depends(get_db)):
    return db.query(Pagamento).filter(Pagamento.cliente_id == cliente_id).all()


# --> objetivos
@router.post("/prontuario/{cliente_id}/objetivos")
def criar_objetivo(cliente_id: int, objetivo: dict, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    novo = Objetivo(cliente_id=cliente_id, nutricionista_id=cliente.nutricionista_id or 0, **objetivo)
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo


@router.get("/prontuario/{cliente_id}/objetivos")
def listar_objetivos(cliente_id: int, db: Session = Depends(get_db)):
    return db.query(Objetivo).filter(Objetivo.cliente_id == cliente_id).all()


# --> avancos
@router.post("/prontuario/{cliente_id}/avancos")
def criar_avanco(cliente_id: int, avanco: dict, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    novo = Avanco(cliente_id=cliente_id, nutricionista_id=cliente.nutricionista_id or 0, **avanco)
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo


@router.get("/prontuario/{cliente_id}/avancos")
def listar_avancos(cliente_id: int, db: Session = Depends(get_db)):
    return db.query(Avanco).filter(Avanco.cliente_id == cliente_id).all()


# --> prontuário full
@router.get("/prontuario/{cliente_id}/full")
def prontuario_full(cliente_id: int, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    conversas = db.query(Conversa).filter(Conversa.cliente_id == cliente_id).all()
    return {
        "cliente": {
            "id": cliente.id,
            "nome": cliente.nome,
            "status": cliente.status,
            "historico": cliente.historico,
        },
        "conversas": conversas,
        "exames": db.query(Exame).filter(Exame.cliente_id == cliente_id).all(),
        "planos": db.query(PlanoAlimentar).filter(PlanoAlimentar.cliente_id == cliente_id).all(),
        "pagamentos": db.query(Pagamento).filter(Pagamento.cliente_id == cliente_id).all(),
        "objetivos": db.query(Objetivo).filter(Objetivo.cliente_id == cliente_id).all(),
        "avancos": db.query(Avanco).filter(Avanco.cliente_id == cliente_id).all(),
        "arquivos": db.query(Arquivo).filter(Arquivo.cliente_id == cliente_id).all(),
    }
