"""
Datenbank-Konfiguration und Session-Management
PostgreSQL mit SQLAlchemy
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from app.core.config import settings

# SQLAlchemy Engine
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    pool_pre_ping=True,  # Prüfe Verbindung vor Verwendung
    pool_size=10,
    max_overflow=20
)

# Session Factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base Class für Modelle
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency für FastAPI
    Stellt DB-Session bereit und schließt sie nach Verwendung

    Yields:
        Database Session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Initialisiert die Datenbank
    Erstellt alle Tabellen
    """
    Base.metadata.create_all(bind=engine)
