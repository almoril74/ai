"""
Patienten-Management-Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.patient import PatientCreate, PatientUpdate, PatientResponse, PatientListItem
from app.models.patient import Patient
from app.models.user import User, UserRole
from app.security.authentication import get_current_active_user, require_role
from app.security.encryption import encryption_service
from app.security.audit import audit_logger, AuditAction

router = APIRouter(prefix="/patients", tags=["Patienten"])


@router.get("/", response_model=List[PatientListItem])
async def list_patients(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Listet alle Patienten auf (mit reduzierten Daten)

    Args:
        skip: Anzahl zu überspringender Einträge
        limit: Maximale Anzahl zurückzugebender Einträge

    Returns:
        Liste von Patienten
    """
    patients = db.query(Patient).filter(
        Patient.is_active == True
    ).offset(skip).limit(limit).all()

    # Entschlüssele nur Basis-Daten für Liste
    result = []
    for patient in patients:
        try:
            result.append(PatientListItem(
                id=patient.id,
                pseudonym_id=patient.pseudonym_id,
                vorname=encryption_service.decrypt_field(patient.vorname),
                nachname=encryption_service.decrypt_field(patient.nachname),
                geburtsdatum=encryption_service.decrypt_field(patient.geburtsdatum),
                is_active=patient.is_active,
                last_accessed_at=patient.last_accessed_at
            ))
        except Exception as e:
            # Bei Entschlüsselungsfehler überspringen
            continue

    return result


@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: int,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Ruft Details eines Patienten ab

    Args:
        patient_id: ID des Patienten

    Returns:
        Patienten-Details (entschlüsselt)
    """
    patient = db.query(Patient).filter(Patient.id == patient_id).first()

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient nicht gefunden"
        )

    # Audit-Log: Zugriff auf Patientendaten
    client_ip = request.client.host if request.client else "unknown"
    audit_logger.log_patient_access(
        user_id=current_user.id,
        patient_id=patient.pseudonym_id,
        action=AuditAction.PATIENT_VIEWED,
        ip_address=client_ip
    )

    # Update Last-Accessed
    patient.last_accessed_at = db.func.now()
    db.commit()

    # Entschlüssele Daten
    decrypted_data = {
        "id": patient.id,
        "pseudonym_id": patient.pseudonym_id,
        "vorname": encryption_service.decrypt_field(patient.vorname),
        "nachname": encryption_service.decrypt_field(patient.nachname),
        "geburtsdatum": encryption_service.decrypt_field(patient.geburtsdatum),
        "adresse": encryption_service.decrypt_field(patient.adresse) if patient.adresse else None,
        "telefon": encryption_service.decrypt_field(patient.telefon) if patient.telefon else None,
        "email": encryption_service.decrypt_field(patient.email) if patient.email else None,
        "anamnese": encryption_service.decrypt_field(patient.anamnese) if patient.anamnese else None,
        "allergien": encryption_service.decrypt_field(patient.allergien) if patient.allergien else None,
        "medikation": encryption_service.decrypt_field(patient.medikation) if patient.medikation else None,
        "vorerkrankungen": encryption_service.decrypt_field(patient.vorerkrankungen) if patient.vorerkrankungen else None,
        "is_active": patient.is_active,
        "consent_given": patient.consent_given,
        "consent_date": patient.consent_date,
        "imported_from_simplimed": patient.imported_from_simplimed,
        "created_at": patient.created_at,
        "updated_at": patient.updated_at
    }

    return PatientResponse(**decrypted_data)


@router.post("/", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def create_patient(
    patient_data: PatientCreate,
    request: Request,
    current_user: User = Depends(require_role(UserRole.ASSISTANT)),
    db: Session = Depends(get_db)
):
    """
    Erstellt neuen Patienten

    Args:
        patient_data: Patientendaten

    Returns:
        Erstellter Patient
    """
    # Generiere Pseudonym-ID
    unique_string = f"{patient_data.nachname}_{patient_data.vorname}_{patient_data.geburtsdatum}"
    pseudonym_id = encryption_service.hash_patient_id(unique_string)

    # Prüfe ob Patient bereits existiert
    existing = db.query(Patient).filter(Patient.pseudonym_id == pseudonym_id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Patient existiert bereits"
        )

    # Verschlüssele alle Daten
    patient = Patient(
        pseudonym_id=pseudonym_id,
        vorname=encryption_service.encrypt_field(patient_data.vorname),
        nachname=encryption_service.encrypt_field(patient_data.nachname),
        geburtsdatum=encryption_service.encrypt_field(patient_data.geburtsdatum),
        adresse=encryption_service.encrypt_field(patient_data.adresse) if patient_data.adresse else None,
        telefon=encryption_service.encrypt_field(patient_data.telefon) if patient_data.telefon else None,
        email=encryption_service.encrypt_field(patient_data.email) if patient_data.email else None,
        anamnese=encryption_service.encrypt_field(patient_data.anamnese) if patient_data.anamnese else None,
        allergien=encryption_service.encrypt_field(patient_data.allergien) if patient_data.allergien else None,
        medikation=encryption_service.encrypt_field(patient_data.medikation) if patient_data.medikation else None,
        vorerkrankungen=encryption_service.encrypt_field(patient_data.vorerkrankungen) if patient_data.vorerkrankungen else None,
        consent_given=patient_data.consent_given,
        is_active=True
    )

    db.add(patient)
    db.commit()
    db.refresh(patient)

    # Audit-Log
    client_ip = request.client.host if request.client else "unknown"
    audit_logger.log_patient_access(
        user_id=current_user.id,
        patient_id=patient.pseudonym_id,
        action=AuditAction.PATIENT_CREATED,
        ip_address=client_ip
    )

    # Entschlüssele für Response
    return await get_patient(patient.id, request, current_user, db)


@router.put("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: int,
    patient_data: PatientUpdate,
    request: Request,
    current_user: User = Depends(require_role(UserRole.ASSISTANT)),
    db: Session = Depends(get_db)
):
    """
    Aktualisiert Patientendaten

    Args:
        patient_id: ID des Patienten
        patient_data: Neue Daten

    Returns:
        Aktualisierter Patient
    """
    patient = db.query(Patient).filter(Patient.id == patient_id).first()

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient nicht gefunden"
        )

    # Update nur gesetzte Felder
    update_data = patient_data.dict(exclude_unset=True)

    for field, value in update_data.items():
        if value is not None:
            # Verschlüssele Wert
            encrypted_value = encryption_service.encrypt_field(str(value))
            setattr(patient, field, encrypted_value)

    db.commit()
    db.refresh(patient)

    # Audit-Log
    client_ip = request.client.host if request.client else "unknown"
    audit_logger.log_patient_access(
        user_id=current_user.id,
        patient_id=patient.pseudonym_id,
        action=AuditAction.PATIENT_UPDATED,
        ip_address=client_ip
    )

    return await get_patient(patient.id, request, current_user, db)


@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_patient(
    patient_id: int,
    request: Request,
    current_user: User = Depends(require_role(UserRole.DOCTOR)),
    db: Session = Depends(get_db)
):
    """
    Löscht Patienten (soft delete)

    Args:
        patient_id: ID des Patienten
    """
    patient = db.query(Patient).filter(Patient.id == patient_id).first()

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient nicht gefunden"
        )

    # Soft Delete
    patient.is_active = False
    patient.marked_for_deletion = True
    db.commit()

    # Audit-Log
    client_ip = request.client.host if request.client else "unknown"
    audit_logger.log_patient_access(
        user_id=current_user.id,
        patient_id=patient.pseudonym_id,
        action=AuditAction.PATIENT_DELETED,
        ip_address=client_ip
    )

    return None
