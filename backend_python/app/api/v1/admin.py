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
from app.domain.models.admin_request import AdminRequest
from app.db import get_db
from app.api.v1.auth import get_current_user
from app.workers.admin_monitor_worker import coletar_metricas, notificar_admins
import datetime

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
def listar_arquivos(db: Session = Depends(get_db), current_user: Nutricionista = Depends(get_current_user)):
    if current_user.papel not in ["admin"]:
        raise HTTPException(status_code=403, detail="Acesso negado")
    return db.query(Arquivo).all()


@router.get("/admin/metrics")
def metrics(current_user: Nutricionista = Depends(get_current_user)):
    if current_user.papel not in ["admin"]:
        raise HTTPException(status_code=403, detail="Acesso negado")
    return colectar_metricas()


@router.post("/admin/notifications")
def enviar_notificacao(texto: str, current_user: Nutricionista = Depends(get_current_user)):
    if current_user.papel not in ["admin"]:
        raise HTTPException(status_code=403, detail="Acesso negado")
    notificar_admins(texto)
    return {"status": "notificado"}


@router.post("/admin/requests")
def criar_pedido_admin(tenant_id: int, tipo: str, descricao: str, nutricionista_id: int = None, db: Session = Depends(get_db), current_user: Nutricionista = Depends(get_current_user)):
    if current_user.papel not in ["admin"]:
        raise HTTPException(status_code=403, detail="Acesso negado")
    req = AdminRequest(
        tenant_id=tenant_id,
        nutricionista_id=nutricionista_id,
        tipo=tipo,
        descricao=descricao,
        status="pendente",
        criado_em=datetime.datetime.utcnow(),
        atualizado_em=datetime.datetime.utcnow(),
    )
    db.add(req)
    db.commit()
    db.refresh(req)
    notificar_admins(f"Novo pedido admin: {tipo} (tenant {tenant_id})")
    return req


@router.get("/admin/requests")
def listar_pedidos_admin(db: Session = Depends(get_db), current_user: Nutricionista = Depends(get_current_user)):
    if current_user.papel not in ["admin"]:
        raise HTTPException(status_code=403, detail="Acesso negado")
    return db.query(AdminRequest).order_by(AdminRequest.criado_em.desc()).all()


@router.put("/admin/requests/{request_id}")
def atualizar_pedido_admin(request_id: int, status: str, db: Session = Depends(get_db), current_user: Nutricionista = Depends(get_current_user)):
    if current_user.papel not in ["admin"]:
        raise HTTPException(status_code=403, detail="Acesso negado")
    pedido = db.query(AdminRequest).filter(AdminRequest.id == request_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    pedido.status = status
    pedido.atualizado_em = datetime.datetime.utcnow()
    db.commit()
    db.refresh(pedido)
    return pedido