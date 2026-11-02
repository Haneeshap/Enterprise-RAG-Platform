import os
import uuid
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://rag:rag@localhost:5432/rag",
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=3600)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency to get DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Create tables on import
def init_db():
    """Initialize database tables."""
    from sqlalchemy import MetaData

    metadata = MetaData()

    # Docs table
    metadata.create_all(engine, tables=[...])  # Will be handled by Alembic/migrations