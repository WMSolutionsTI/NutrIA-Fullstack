from app.workers.quebrar_enviar_mensagens_worker import enviar_mensagens
from app.domain.models.nutricionista import Nutricionista
from app.domain.models.contabilidade import Contabilidade
from app.domain.models.cliente import Cliente
from app.domain.models.relatorio import Relatorio
from app.database import get_db
from sqlalchemy.orm import Session

# Handler para processar comandos do nutricionista via Chatwoot

def process_comando_chatwoot(account_id, conversation_id, comando, nutri_id, db: Session):
    nutri = db.query(Nutricionista).filter(Nutricionista.id == nutri_id).first()
    if not nutri:
        enviar_mensagens(account_id, conversation_id, ["Nutricionista não encontrado."])
        return
    tenant_id = nutri.tenant_id

    if comando == "saldo":
        receitas = db.query(Contabilidade).filter(Contabilidade.tenant_id == tenant_id, Contabilidade.tipo == "receita").all()
        despesas = db.query(Contabilidade).filter(Contabilidade.tenant_id == tenant_id, Contabilidade.tipo == "despesa").all()
        total_receitas = sum(r.valor for r in receitas)
        total_despesas = sum(d.valor for d in despesas)
        saldo = total_receitas - total_despesas
        msg = f"Saldo atual: R$ {saldo}\nReceitas: R$ {total_receitas}\nDespesas: R$ {total_despesas}"
        enviar_mensagens(account_id, conversation_id, [msg])
    elif comando == "clientes":
        clientes = db.query(Cliente).filter(Cliente.nutricionista_id == nutri_id).all()
        total_clientes = len(clientes)
        msg = f"Total de clientes: {total_clientes}"
        enviar_mensagens(account_id, conversation_id, [msg])
    elif comando == "relatorios":
        relatorios = db.query(Relatorio).filter(Relatorio.tenant_id == tenant_id).all()
        total_relatorios = len(relatorios)
        msg = f"Total de relatórios: {total_relatorios}"
        enviar_mensagens(account_id, conversation_id, [msg])
    else:
        enviar_mensagens(account_id, conversation_id, ["Comando não reconhecido. Use: saldo, clientes, relatórios."])
