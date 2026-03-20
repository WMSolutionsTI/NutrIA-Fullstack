from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.domain.models.cliente import Cliente
from app.domain.models.arquivo import Arquivo
from app.database import get_db

router = APIRouter()

@router.post("/exames/{cliente_id}/solicitar")
def solicitar_exame(cliente_id: int, exame_nome: str, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    # Mock: solicitação
    return {"cliente_id": cliente.id, "exame": exame_nome, "status": "solicitado"}

@router.post("/exames/{cliente_id}/upload")
def upload_resultado_exame(cliente_id: int, arquivo_id: int, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    arquivo = db.query(Arquivo).filter(Arquivo.id == arquivo_id).first()
    if not cliente or not arquivo:
        raise HTTPException(status_code=404, detail="Cliente ou arquivo não encontrado")
    # Mock: upload resultado
    return {"cliente_id": cliente.id, "arquivo_id": arquivo.id, "status": "resultado anexado"}

@router.post("/exames/{cliente_id}/ia")
def analisar_exame_ia(cliente_id: int, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    # Mock: análise IA
    return {"cliente_id": cliente.id, "analise_ia": "Análise realizada por IA"}

@router.get("/exames/{cliente_id}/historico")
def historico_exames(cliente_id: int, db: Session = Depends(get_db)):
    # Mock: histórico
    return {"cliente_id": cliente_id, "historico": ["Exame 1", "Exame 2"]}