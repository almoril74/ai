"""
Patienten-Modell mit DSGVO-konformer Datenspeicherung
Alle sensitiven Felder werden verschlüsselt
"""

from sqlalchemy import Column, Integer, String, Date, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, timedelta

from app.core.database import Base
from app.core.config import settings


class Patient(Base):
    """
    Patienten-Modell mit verschlüsselten Gesundheitsdaten

    DSGVO Art. 9 - Besondere Kategorien personenbezogener Daten
    § 630f BGB - Aufbewahrungsfrist 10 Jahre
    """
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)

    # Pseudonymisierte ID (Hash der Original-ID aus SimpliMed)
    pseudonym_id = Column(String(64), unique=True, nullable=False, index=True)

    # Verschlüsselte persönliche Daten
    # Diese Felder werden mit encryption_service verschlüsselt
    vorname = Column(Text, nullable=False)  # Encrypted
    nachname = Column(Text, nullable=False)  # Encrypted
    geburtsdatum = Column(Text, nullable=False)  # Encrypted (als String gespeichert)

    # Verschlüsselte Kontaktdaten
    adresse = Column(Text, nullable=True)  # Encrypted
    telefon = Column(Text, nullable=True)  # Encrypted
    email = Column(Text, nullable=True)  # Encrypted

    # Verschlüsselte medizinische Daten
    anamnese = Column(Text, nullable=True)  # Encrypted - Krankengeschichte
    allergien = Column(Text, nullable=True)  # Encrypted
    medikation = Column(Text, nullable=True)  # Encrypted - Aktuelle Medikamente
    vorerkrankungen = Column(Text, nullable=True)  # Encrypted

    # Nicht-sensitive Metadaten
    is_active = Column(Boolean, default=True, nullable=False)

    # SimpliMed-Integration
    simplimed_id = Column(String(50), nullable=True, index=True)  # Original SimpliMed-ID (falls benötigt)
    imported_from_simplimed = Column(Boolean, default=False, nullable=False)
    simplimed_import_date = Column(DateTime, nullable=True)

    # DSGVO-Einwilligung
    consent_given = Column(Boolean, default=False, nullable=False)
    consent_date = Column(DateTime, nullable=True)

    # Aufbewahrungsfrist (§ 630f BGB - 10 Jahre)
    retention_until = Column(DateTime, nullable=True)
    marked_for_deletion = Column(Boolean, default=False, nullable=False)

    # Zeitstempel
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    last_accessed_at = Column(DateTime, nullable=True)

    # Beziehungen
    treatments = relationship("Treatment", back_populates="patient", cascade="all, delete-orphan")
    consents = relationship("Consent", back_populates="patient", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Patient(id={self.id}, pseudonym_id='{self.pseudonym_id}')>"

    def calculate_retention_date(self) -> datetime:
        """
        Berechnet Aufbewahrungsfrist gem. § 630f BGB
        10 Jahre ab letzter Behandlung

        Returns:
            Datum bis zu dem Daten aufbewahrt werden müssen
        """
        # Standard: 10 Jahre ab Erstellung
        retention_years = settings.DATA_RETENTION_YEARS
        return self.created_at + timedelta(days=retention_years * 365)

    def should_be_deleted(self) -> bool:
        """
        Prüft ob Patient gelöscht werden kann

        Returns:
            True wenn Aufbewahrungsfrist abgelaufen
        """
        if not self.retention_until:
            self.retention_until = self.calculate_retention_date()

        return datetime.utcnow() > self.retention_until

    @property
    def display_name(self) -> str:
        """Pseudonymisierter Anzeigename (ohne Entschlüsselung)"""
        return f"Patient-{self.pseudonym_id[:8]}"
