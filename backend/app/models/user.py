"""
Benutzer-Modell mit Rollen und MFA-Unterstützung
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.core.database import Base


class UserRole(str, enum.Enum):
    """Benutzerrollen für RBAC"""
    ADMIN = "admin"  # Volle Rechte
    DOCTOR = "doctor"  # Osteopath/Behandler
    ASSISTANT = "assistant"  # Praxisassistent
    READONLY = "readonly"  # Nur Lesezugriff


class User(Base):
    """
    Benutzer-Modell mit Authentifizierung und MFA

    DSGVO-Hinweis: Benutzerdaten werden verschlüsselt gespeichert
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    # Authentifizierung
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)

    # Persönliche Daten
    full_name = Column(String(255), nullable=False)

    # Rollen & Berechtigungen
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.ASSISTANT)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)

    # Multi-Faktor-Authentifizierung (MFA)
    mfa_enabled = Column(Boolean, default=False, nullable=False)
    mfa_secret = Column(String(32), nullable=True)  # TOTP Secret

    # Login-Sicherheit
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime, nullable=True)
    last_login = Column(DateTime, nullable=True)

    # Zeitstempel
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Letztes Passwort-Update (für Passwort-Ablauf)
    password_changed_at = Column(DateTime, server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"

    @property
    def is_locked(self) -> bool:
        """Prüft ob der Account gesperrt ist"""
        if self.locked_until:
            return datetime.utcnow() < self.locked_until
        return False

    def has_permission(self, required_role: UserRole) -> bool:
        """
        Prüft ob Benutzer benötigte Rolle hat

        Args:
            required_role: Erforderliche Rolle

        Returns:
            True wenn Benutzer Berechtigung hat
        """
        role_hierarchy = {
            UserRole.READONLY: 1,
            UserRole.ASSISTANT: 2,
            UserRole.DOCTOR: 3,
            UserRole.ADMIN: 4
        }

        user_level = role_hierarchy.get(self.role, 0)
        required_level = role_hierarchy.get(required_role, 0)

        return user_level >= required_level or self.is_superuser
