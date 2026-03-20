from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.domain.models.cliente import Cliente
from app.domain.models.arquivo import Arquivo
from app.database import get_db

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