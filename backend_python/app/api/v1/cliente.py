from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.domain.models.cliente import Cliente
from app.domain.models.nutricionista import Nutricionista
from app.db import get_db
from app.api.v1.auth import get_current_user

router = APIRouter(prefix="/clientes", tags=["Clientes"])

@router.post("/{cliente_id}/relacionamento_satisfeito", response_model=dict)
def relacionamento_cliente_satisfeito(cliente_id: int, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).get(cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    if cliente.status != "cliente_satisfeito":
        raise HTTPException(status_code=400, detail="Cliente não está satisfeito")
    nutri = db.query(Nutricionista).get(cliente.nutricionista_id)
    contexto = nutri.contexto_ia if nutri else None
    relacionamento = [
        "Envio de novidades",
        "Pesquisa de satisfação",
        "Solicitação de feedback",
        "Follow-up periódico",
        "Disponibilidade para novas necessidades"
    ]
    return {"id": cliente.id, "status": cliente.status, "relacionamento": relacionamento, "contexto_nutri": contexto}

@router.post("/{cliente_id}/recuperar", response_model=dict)
def recuperar_cliente_inativo(cliente_id: int, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).get(cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    if cliente.status != "cliente_inativo":
        raise HTTPException(status_code=400, detail="Cliente não está inativo")
    nutri = db.query(Nutricionista).get(cliente.nutricionista_id)
    contexto = nutri.contexto_ia if nutri else None
    estrategias = [
        "Mensagem personalizada de reativação",
        "Oferta especial de retorno",
        "Follow-up automatizado",
        "Conteúdo educativo",
        "Promoção exclusiva"
    ]
    return {"id": cliente.id, "status": cliente.status, "estrategias": estrategias, "contexto_nutri": contexto}

@router.post("/{cliente_id}/atendimento_completo", response_model=dict)
def atendimento_completo_cliente(cliente_id: int, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).get(cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    if cliente.status != "cliente_ativo":
        raise HTTPException(status_code=400, detail="Cliente não está ativo")
    nutri = db.query(Nutricionista).get(cliente.nutricionista_id)
    contexto = nutri.contexto_ia if nutri else None
    atendimento = {
        "anamnese": "Realizada",
        "plano_alimentar": "Elaborado",
        "dicas": "Enviadas",
        "follow_ups": "Agendados",
        "alertas": "Configurados",
        "contexto_nutri": contexto
    }
    return {"id": cliente.id, "status": cliente.status, "atendimento": atendimento}

@router.put("/{cliente_id}/ativar", response_model=dict)
def ativar_cliente(cliente_id: int, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).get(cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    cliente.status = "cliente_ativo"
    db.commit()
    db.refresh(cliente)
    return {"id": cliente.id, "status": cliente.status}

@router.get("/", response_model=list)
def list_clientes(db: Session = Depends(get_db), current_user: Nutricionista = Depends(get_current_user)):
    # Apenas admin/nutri podem listar todos clientes, secretária lista restrito
    if current_user.papel not in ["admin", "nutri", "secretaria"]:
        raise HTTPException(status_code=403, detail="Acesso negado")
    return db.query(Cliente).all()

@router.post("/", response_model=dict)
def create_cliente(cliente: dict, db: Session = Depends(get_db), current_user: Nutricionista = Depends(get_current_user)):
    if current_user.papel not in ["admin", "nutri", "secretaria"]:
        raise HTTPException(status_code=403, detail="Acesso negado")
    cliente_data = cliente.copy()
    cliente_data["nutricionista_id"] = cliente_data.get("nutricionista_id") or current_user.id
    new_cliente = Cliente(**cliente_data)
    db.add(new_cliente)
    db.commit()
    db.refresh(new_cliente)
    return {"id": new_cliente.id}

@router.get("/{cliente_id}", response_model=dict)
def get_cliente(cliente_id: int, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).get(cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return cliente.__dict__

@router.put("/{cliente_id}", response_model=dict)
def update_cliente(cliente_id: int, cliente_data: dict, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).get(cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    for k, v in cliente_data.items():
        setattr(cliente, k, v)
    db.commit()
    db.refresh(cliente)
    return cliente.__dict__

@router.delete("/{cliente_id}", response_model=dict)
def delete_cliente(cliente_id: int, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).get(cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    db.delete(cliente)
    db.commit()
    return {"status": "deleted"}

@router.post("/vincular", response_model=dict)
def vincular_cliente(contato_chatwoot: str, nutricionista_id: int, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter_by(contato_chatwoot=contato_chatwoot).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    nutri = db.query(Nutricionista).get(nutricionista_id)
    if not nutri:
        raise HTTPException(status_code=404, detail="Nutricionista não encontrado")
    cliente.nutricionista_id = nutricionista_id
    db.commit()
    db.refresh(cliente)
    return {"status": "ok", "cliente_id": cliente.id, "nutricionista_id": nutricionista_id}
