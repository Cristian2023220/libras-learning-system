import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Lê a URL de conexão da variável de ambiente (Render/PostgreSQL) ou usa SQLite local
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sinaliza.db")

# Ajuste para compatibilidade com o formato postgres:// do Render
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# SQLite requer connect_args específico para suporte multithread
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Dependency para injeção de sessão do banco nas rotas FastAPI."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()