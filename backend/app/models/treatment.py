"""
Behandlungs-Modell für Dokumentationspflicht nach § 630f BGB
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Treatment(Base):
    """
    Behandlungsdokumentation gem. § 630f BGB

    Dokumentationspflicht:
    - Datum und Uhrzeit
    - Anamnese
    - Diagnose
    - Behandlung/Therapie
    - Untersuchungsergebnisse
    - Therapieerfolg
    """
    __tablename__ = "treatments"

    id = Column(Integer, primary_key=True, index=True)

    # Beziehung zum Patienten
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    patient = relationship("Patient", back_populates="treatments")

    # Behandler
    practitioner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    practitioner = relationship("User")

    # Behandlungsdaten (verschlüsselt)
    behandlungsdatum = Column(DateTime, nullable=False, index=True)

    # Verschlüsselte Behandlungsdokumentation
    anamnese = Column(Text, nullable=True)  # Encrypted - Aktuelle Beschwerden
    diagnose = Column(Text, nullable=False)  # Encrypted - Osteopathische Diagnose
    behandlung = Column(Text, nullable=False)  # Encrypted - Durchgeführte Behandlung
    befunde = Column(Text, nullable=True)  # Encrypted - Untersuchungsbefunde
    therapieziel = Column(Text, nullable=True)  # Encrypted
    therapieerfolg = Column(Text, nullable=True)  # Encrypted - Bewertung des Erfolgs
    empfehlungen = Column(Text, nullable=True)  # Encrypted - Empfehlungen für Patienten

    # Weitere Notizen
    notizen = Column(Text, nullable=True)  # Encrypted - Interne Notizen

    # Behandlungsdetails
    dauer_minuten = Column(Integer, nullable=True)  # Behandlungsdauer
    kosten = Column(Numeric(10, 2), nullable=True)  # Kosten/Gebühr

    # Nachbehandlung
    folgebehandlung_empfohlen = Column(String(50), nullable=True)  # z.B. "in 2 Wochen"
    naechster_termin = Column(DateTime, nullable=True)

    # Zeitstempel
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<Treatment(id={self.id}, patient_id={self.patient_id}, datum={self.behandlungsdatum})>"
