"""
Einwilligungs-Modell für DSGVO-Compliance
Art. 9 Abs. 2 lit. a DSGVO - Explizite Einwilligung
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.core.database import Base


class ConsentType(str, enum.Enum):
    """Typen von Einwilligungen"""
    DATA_PROCESSING = "data_processing"  # Datenverarbeitung allgemein
    HEALTH_DATA = "health_data"  # Gesundheitsdaten gem. Art. 9 DSGVO
    MARKETING = "marketing"  # Marketing/Werbung
    THIRD_PARTY = "third_party"  # Weitergabe an Dritte
    DIGITAL_COMMUNICATION = "digital_communication"  # E-Mail/SMS-Kommunikation


class ConsentStatus(str, enum.Enum):
    """Status der Einwilligung"""
    PENDING = "pending"  # Ausstehend
    GIVEN = "given"  # Erteilt
    REVOKED = "revoked"  # Widerrufen
    EXPIRED = "expired"  # Abgelaufen


class Consent(Base):
    """
    Einwilligungsverwaltung gem. Art. 7 DSGVO

    Dokumentiert:
    - Zeitpunkt der Einwilligung
    - Art der Einwilligung
    - Widerrufsmöglichkeit
    - Aktuelle Gültigkeit
    """
    __tablename__ = "consents"

    id = Column(Integer, primary_key=True, index=True)

    # Beziehung zum Patienten
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    patient = relationship("Patient", back_populates="consents")

    # Art der Einwilligung
    consent_type = Column(SQLEnum(ConsentType), nullable=False)
    status = Column(SQLEnum(ConsentStatus), nullable=False, default=ConsentStatus.PENDING)

    # Einwilligungstext (Version für Nachvollziehbarkeit)
    consent_text = Column(Text, nullable=False)  # Der Text, dem zugestimmt wurde
    consent_version = Column(String(20), nullable=False)  # Versionsnummer

    # Zeitstempel
    given_at = Column(DateTime, nullable=True)  # Wann wurde zugestimmt
    revoked_at = Column(DateTime, nullable=True)  # Wann wurde widerrufen
    expires_at = Column(DateTime, nullable=True)  # Optional: Ablaufdatum

    # Nachweis
    ip_address = Column(String(45), nullable=True)  # IPv4/IPv6
    user_agent = Column(String(500), nullable=True)  # Browser-Info

    # Widerruf
    revocation_reason = Column(Text, nullable=True)

    # Zeitstempel
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<Consent(id={self.id}, patient_id={self.patient_id}, type={self.consent_type}, status={self.status})>"

    def is_valid(self) -> bool:
        """
        Prüft ob Einwilligung gültig ist

        Returns:
            True wenn Einwilligung aktuell gültig
        """
        if self.status != ConsentStatus.GIVEN:
            return False

        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False

        return True

    def revoke(self, reason: str = None) -> None:
        """
        Widerruft die Einwilligung

        Args:
            reason: Grund für den Widerruf
        """
        self.status = ConsentStatus.REVOKED
        self.revoked_at = datetime.utcnow()
        if reason:
            self.revocation_reason = reason
