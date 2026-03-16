from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.cliente import Cliente
from app.db import get_db

router = APIRouter(prefix="/clientes", tags=["Clientes"])

@router.get("/", response_model=list)
def list_clientes(db: Session = Depends(get_db)):
    return db.query(Cliente).all()

@router.post("/", response_model=dict)
def create_cliente(cliente: dict, db: Session = Depends(get_db)):
    new_cliente = Cliente(**cliente)
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
    return {"id": cliente.id, "nutricionista_id": nutricionista_id, "status": "vinculado"}

@router.post("/clientes/vincular_chatwoot")
def vincular_cliente_chatwoot(chatwoot_id: str, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.chatwoot_id == chatwoot_id).first()
    if not cliente:
        cliente = Cliente(chatwoot_id=chatwoot_id)
        db.add(cliente)
        db.commit()
        db.refresh(cliente)
    return cliente

@router.get("/clientes/filtro")
def filtrar_clientes(status: str = None, nutricionista_id: int = None, tenant_id: int = None, db: Session = Depends(get_db)):
    query = db.query(Cliente)
    if status:
        query = query.filter(Cliente.status == status)
    if nutricionista_id:
        query = query.filter(Cliente.nutricionista_id == nutricionista_id)
    if tenant_id:
        query = query.join("Nutricionista").filter(Nutricionista.tenant_id == tenant_id)
    return query.all()