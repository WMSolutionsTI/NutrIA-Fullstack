import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.domain.models.base import Base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    future=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)


def init_db() -> None:
    """Cria as tabelas no banco de dados com base nos modelos declarativos."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Depêndencia do FastAPI para obter sessão de banco de dados."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
