"""
Zentrale Konfiguration der Anwendung
Lädt Umgebungsvariablen und stellt Konfigurationsobjekte bereit
"""

from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import List
import secrets


class Settings(BaseSettings):
    """Haupt-Konfigurationsklasse"""

    # Projekt-Info
    PROJECT_NAME: str = "DSGVO-Patientenaktensystem"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"

    # Datenbank
    DATABASE_URL: str = Field(
        default="postgresql://patientenakte:password@localhost:5432/patientenakte_db",
        description="PostgreSQL-Verbindungs-URL"
    )
    DATABASE_ECHO: bool = False

    # Verschlüsselung (KRITISCH: Niemals in Git committen!)
    MASTER_ENCRYPTION_KEY: str = Field(
        ...,  # Required
        description="Master-Schlüssel für Verschlüsselung (32 Bytes Base64)"
    )
    FIELD_ENCRYPTION_KEY: str = Field(
        ...,  # Required
        description="Feld-Verschlüsselungs-Schlüssel (32 Bytes Base64)"
    )

    # JWT & Authentication
    SECRET_KEY: str = Field(
        default_factory=lambda: secrets.token_urlsafe(32),
        description="Secret Key für JWT-Tokens"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Sicherheit
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    MAX_LOGIN_ATTEMPTS: int = 5
    LOGIN_TIMEOUT_MINUTES: int = 30
    SESSION_TIMEOUT_MINUTES: int = 60

    # MFA (Multi-Faktor-Authentifizierung)
    MFA_ENABLED: bool = True
    MFA_ISSUER_NAME: str = "Osteopathie-Praxis"

    # SimpliMed-Integration
    SIMPLIMED_IMPORT_PATH: str = "/opt/simplimed/exports"
    SIMPLIMED_BACKUP_PATH: str = "/opt/backups/simplimed"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "/var/log/patientenakte/app.log"
    AUDIT_LOG_FILE: str = "/var/log/patientenakte/audit.log"

    # Backup & Aufbewahrung
    BACKUP_PATH: str = "/opt/backups/encrypted"
    BACKUP_RETENTION_DAYS: int = 365
    DATA_RETENTION_YEARS: int = 10  # § 630f BGB

    # E-Mail (optional)
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = ""

    # Redis (Session-Management)
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""
    REDIS_DB: int = 0

    # Development
    DEBUG: bool = False
    TESTING: bool = False

    @validator("CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS origins from comma-separated string"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @validator("ALLOWED_HOSTS", pre=True)
    def parse_allowed_hosts(cls, v):
        """Parse allowed hosts from comma-separated string"""
        if isinstance(v, str):
            return [host.strip() for host in v.split(",")]
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Singleton-Instanz der Settings
settings = Settings()


# Validierung bei Import
def validate_security_settings():
    """Validiert sicherheitskritische Einstellungen"""
    errors = []

    if settings.SECRET_KEY == "CHANGE_ME_RANDOM_SECRET_KEY_HERE":
        errors.append("SECRET_KEY muss geändert werden!")

    if settings.MASTER_ENCRYPTION_KEY == "CHANGE_ME_32_BYTE_BASE64_KEY_HERE=":
        errors.append("MASTER_ENCRYPTION_KEY muss generiert werden!")

    if settings.FIELD_ENCRYPTION_KEY == "CHANGE_ME_32_BYTE_BASE64_KEY_HERE=":
        errors.append("FIELD_ENCRYPTION_KEY muss generiert werden!")

    if not settings.DEBUG and settings.DATABASE_URL.startswith("sqlite"):
        errors.append("SQLite sollte nicht in Produktion verwendet werden!")

    if errors:
        error_msg = "\n".join(["SICHERHEITS-FEHLER:"] + errors)
        raise ValueError(error_msg)


# Führe Validierung aus (außer bei Tests)
if not settings.TESTING:
    try:
        validate_security_settings()
    except ValueError:
        # In Entwicklung nur Warning, in Produktion Fehler
        if not settings.DEBUG:
            raise
