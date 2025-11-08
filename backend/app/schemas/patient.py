"""Patient Schemas"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class PatientBase(BaseModel):
    """Basis-Schema für Patienten"""
    vorname: str
    nachname: str
    geburtsdatum: str  # Format: YYYY-MM-DD
    adresse: Optional[str] = None
    telefon: Optional[str] = None
    email: Optional[str] = None
    anamnese: Optional[str] = None
    allergien: Optional[str] = None
    medikation: Optional[str] = None
    vorerkrankungen: Optional[str] = None


class PatientCreate(PatientBase):
    """Schema für Patienten-Erstellung"""
    consent_given: bool = False


class PatientUpdate(BaseModel):
    """Schema für Patienten-Update"""
    vorname: Optional[str] = None
    nachname: Optional[str] = None
    geburtsdatum: Optional[str] = None
    adresse: Optional[str] = None
    telefon: Optional[str] = None
    email: Optional[str] = None
    anamnese: Optional[str] = None
    allergien: Optional[str] = None
    medikation: Optional[str] = None
    vorerkrankungen: Optional[str] = None


class PatientResponse(PatientBase):
    """Schema für Patienten-Response (entschlüsselte Daten)"""
    id: int
    pseudonym_id: str
    is_active: bool
    consent_given: bool
    consent_date: Optional[datetime] = None
    imported_from_simplimed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PatientListItem(BaseModel):
    """Schema für Patienten-Liste (reduzierte Daten)"""
    id: int
    pseudonym_id: str
    vorname: str
    nachname: str
    geburtsdatum: str
    is_active: bool
    last_accessed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
