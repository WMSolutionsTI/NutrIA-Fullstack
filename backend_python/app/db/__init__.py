import os
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from app.domain.models.base import Base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    future=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)


def _ensure_column(table_name: str, column_name: str, ddl_fragment: str) -> None:
    inspector = inspect(engine)
    try:
        columns = {c["name"] for c in inspector.get_columns(table_name)}
    except Exception:
        return
    if column_name in columns:
        return
    try:
        with engine.begin() as conn:
            conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {ddl_fragment}"))
    except Exception:
        # Mantém bootstrap resiliente em bancos que já tenham schema divergente.
        pass


def _run_lightweight_backfill() -> None:
    try:
        with engine.begin() as conn:
            conn.execute(
                text(
                    "UPDATE chatwoot_accounts "
                    "SET chatwoot_account_external_id = chatwoot_account_id "
                    "WHERE chatwoot_account_external_id IS NULL AND chatwoot_account_id IS NOT NULL"
                )
            )
            conn.execute(
                text(
                    "CREATE UNIQUE INDEX IF NOT EXISTS idx_chatwoot_accounts_external_id "
                    "ON chatwoot_accounts(chatwoot_account_external_id)"
                )
            )
    except Exception:
        pass


def init_db() -> None:
    """Cria as tabelas no banco de dados com base nos modelos declarativos."""
    # Garantir importação de todos os models para registro no metadata
    from app.domain.models import (
        agenda_evento,
        admin_request,
        arquivo,
        arquivo_dispatch,
        avanco,
        caixa_de_entrada,
        campanha,
        chatwoot_account,
        cliente,
        contabilidade,
        conversa,
        exame,
        google_calendar_integration,
        nutricionista,
        nutri_action_confirmation,
        nutri_contact_verification,
        objetivo,
        pagamento,
        plano_alimentar,
        prompt,
        relatorio,
        tenant,
        voice_call,
        worker_job,
    )

    Base.metadata.create_all(bind=engine)
    _ensure_column("chatwoot_accounts", "chatwoot_account_external_id", "chatwoot_account_external_id VARCHAR")
    _ensure_column("conversas", "chatwoot_account_id", "chatwoot_account_id VARCHAR")
    _ensure_column("conversas", "chatwoot_inbox_id", "chatwoot_inbox_id VARCHAR")
    _ensure_column("conversas", "canal_origem", "canal_origem VARCHAR")
    _ensure_column("conversas", "chatwoot_conversation_id", "chatwoot_conversation_id VARCHAR")
    _run_lightweight_backfill()


def get_db():
    """Depêndencia do FastAPI para obter sessão de banco de dados."""
    init_db()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
