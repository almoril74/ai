"""
SimpliMed CSV-Import-Service mit Verschlüsselung
Importiert Patientendaten aus SimpliMed-Exporten
"""

import csv
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
import shutil
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.patient import Patient
from app.security.encryption import encryption_service
from app.security.audit import audit_logger, AuditAction


class SimpliMedImporter:
    """
    Service für Import von SimpliMed-Patientendaten

    SimpliMed CSV-Format (typische Felder):
    - PatientenNr
    - Name (Nachname)
    - Vorname
    - Geburtsdatum
    - Adresse
    - PLZ
    - Ort
    - Telefon
    - Email
    - Anamnese
    - Diagnosen
    - etc.
    """

    def __init__(self, db: Session):
        """
        Initialisiert Importer

        Args:
            db: Datenbank-Session
        """
        self.db = db
        self.import_stats = {
            'total': 0,
            'imported': 0,
            'updated': 0,
            'skipped': 0,
            'errors': 0
        }

    def import_from_csv(
        self,
        csv_path: str,
        delimiter: str = ';',
        encoding: str = 'utf-8',
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Importiert Patientendaten aus SimpliMed CSV

        Args:
            csv_path: Pfad zur CSV-Datei
            delimiter: CSV-Trennzeichen (meist ;)
            encoding: Dateikodierung
            user_id: ID des importierenden Benutzers

        Returns:
            Import-Statistik
        """
        csv_file = Path(csv_path)

        if not csv_file.exists():
            raise FileNotFoundError(f"CSV-Datei nicht gefunden: {csv_path}")

        # Backup der Original-Datei
        self._backup_import_file(csv_file)

        # CSV einlesen mit Pandas (bessere Encoding-Behandlung)
        try:
            df = pd.read_csv(
                csv_file,
                delimiter=delimiter,
                encoding=encoding,
                dtype=str  # Alle als String einlesen
            )
        except Exception as e:
            raise ValueError(f"CSV-Parsing fehlgeschlagen: {str(e)}")

        self.import_stats['total'] = len(df)

        # Jede Zeile verarbeiten
        for index, row in df.iterrows():
            try:
                self._import_patient_row(row, user_id)
            except Exception as e:
                print(f"Fehler bei Zeile {index + 1}: {str(e)}")
                self.import_stats['errors'] += 1

        # Audit-Log
        if user_id:
            audit_logger.log_event(
                user_id=user_id,
                action=AuditAction.SIMPLIMED_IMPORT,
                resource_type="import",
                success=True,
                additional_data=self.import_stats
            )

        return self.import_stats

    def _import_patient_row(self, row: pd.Series, user_id: Optional[int]) -> None:
        """
        Importiert eine einzelne Patienten-Zeile

        Args:
            row: Pandas Series mit Patientendaten
            user_id: ID des importierenden Benutzers
        """
        # SimpliMed-Patienten-ID (oder generiere aus Namen)
        simplimed_id = self._get_field(row, ['PatientenNr', 'Patientennummer', 'ID'])

        if not simplimed_id:
            # Generiere ID aus Namen wenn nicht vorhanden
            vorname = self._get_field(row, ['Vorname', 'FirstName'])
            nachname = self._get_field(row, ['Name', 'Nachname', 'LastName'])
            simplimed_id = f"{nachname}_{vorname}_{datetime.now().timestamp()}"

        # Prüfe ob Patient bereits existiert
        pseudonym_id = encryption_service.hash_patient_id(simplimed_id)
        existing_patient = self.db.query(Patient).filter(
            Patient.pseudonym_id == pseudonym_id
        ).first()

        if existing_patient:
            # Update bestehender Patient
            self._update_patient(existing_patient, row)
            self.import_stats['updated'] += 1
        else:
            # Neuer Patient
            self._create_patient(row, simplimed_id, pseudonym_id)
            self.import_stats['imported'] += 1

        self.db.commit()

    def _create_patient(self, row: pd.Series, simplimed_id: str, pseudonym_id: str) -> Patient:
        """
        Erstellt neuen Patienten aus CSV-Zeile

        Args:
            row: CSV-Zeile
            simplimed_id: Original SimpliMed-ID
            pseudonym_id: Hash der ID

        Returns:
            Neuer Patient
        """
        # Extrahiere Felder aus CSV
        vorname = self._get_field(row, ['Vorname', 'FirstName']) or ""
        nachname = self._get_field(row, ['Name', 'Nachname', 'LastName']) or ""
        geburtsdatum = self._get_field(row, ['Geburtsdatum', 'Birthdate', 'GebDatum']) or ""

        # Adresse zusammensetzen
        strasse = self._get_field(row, ['Adresse', 'Strasse', 'Street']) or ""
        plz = self._get_field(row, ['PLZ', 'Postleitzahl']) or ""
        ort = self._get_field(row, ['Ort', 'Stadt', 'City']) or ""
        adresse = f"{strasse}, {plz} {ort}".strip(', ')

        telefon = self._get_field(row, ['Telefon', 'Tel', 'Phone']) or ""
        email = self._get_field(row, ['Email', 'E-Mail', 'EMail']) or ""

        # Medizinische Daten
        anamnese = self._get_field(row, ['Anamnese', 'Beschwerden', 'Complaints']) or ""
        allergien = self._get_field(row, ['Allergien', 'Allergies']) or ""
        medikation = self._get_field(row, ['Medikation', 'Medikamente', 'Medication']) or ""
        vorerkrankungen = self._get_field(row, ['Vorerkrankungen', 'PreviousIllnesses']) or ""

        # Verschlüssele alle sensitiven Daten
        patient = Patient(
            pseudonym_id=pseudonym_id,
            simplimed_id=simplimed_id,
            imported_from_simplimed=True,
            simplimed_import_date=datetime.utcnow(),

            # Verschlüsselte persönliche Daten
            vorname=encryption_service.encrypt_field(vorname),
            nachname=encryption_service.encrypt_field(nachname),
            geburtsdatum=encryption_service.encrypt_field(geburtsdatum),

            # Verschlüsselte Kontaktdaten
            adresse=encryption_service.encrypt_field(adresse) if adresse else None,
            telefon=encryption_service.encrypt_field(telefon) if telefon else None,
            email=encryption_service.encrypt_field(email) if email else None,

            # Verschlüsselte medizinische Daten
            anamnese=encryption_service.encrypt_field(anamnese) if anamnese else None,
            allergien=encryption_service.encrypt_field(allergien) if allergien else None,
            medikation=encryption_service.encrypt_field(medikation) if medikation else None,
            vorerkrankungen=encryption_service.encrypt_field(vorerkrankungen) if vorerkrankungen else None,

            # Noch keine Einwilligung (muss nachgeholt werden!)
            consent_given=False,
            is_active=True
        )

        self.db.add(patient)
        return patient

    def _update_patient(self, patient: Patient, row: pd.Series) -> None:
        """
        Aktualisiert bestehenden Patienten

        Args:
            patient: Bestehender Patient
            row: Neue Daten aus CSV
        """
        # Bei Update nur nicht-leere Felder aktualisieren
        # Bestehende verschlüsselte Daten bleiben erhalten wenn CSV leer

        vorname = self._get_field(row, ['Vorname', 'FirstName'])
        if vorname:
            patient.vorname = encryption_service.encrypt_field(vorname)

        nachname = self._get_field(row, ['Name', 'Nachname', 'LastName'])
        if nachname:
            patient.nachname = encryption_service.encrypt_field(nachname)

        # Weitere Felder analog...
        # (In Produktion: vollständige Update-Logik)

    def _get_field(self, row: pd.Series, field_names: List[str]) -> Optional[str]:
        """
        Holt Feld aus Row mit mehreren möglichen Namen

        Args:
            row: Pandas Series
            field_names: Liste möglicher Feldnamen

        Returns:
            Feldwert oder None
        """
        for field_name in field_names:
            if field_name in row.index:
                value = row[field_name]
                # Pandas NaN zu None
                if pd.isna(value):
                    return None
                return str(value).strip()
        return None

    def _backup_import_file(self, csv_file: Path) -> None:
        """
        Erstellt Backup der Import-Datei

        Args:
            csv_file: CSV-Datei
        """
        backup_dir = Path(settings.SIMPLIMED_BACKUP_PATH)
        backup_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = backup_dir / f"{csv_file.stem}_{timestamp}{csv_file.suffix}"

        shutil.copy2(csv_file, backup_file)

    def validate_csv_structure(self, csv_path: str, delimiter: str = ';') -> Dict[str, Any]:
        """
        Validiert CSV-Struktur vor Import

        Args:
            csv_path: Pfad zur CSV
            delimiter: Trennzeichen

        Returns:
            Validierungsergebnis
        """
        result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'columns': [],
            'row_count': 0
        }

        try:
            df = pd.read_csv(csv_path, delimiter=delimiter, nrows=0)
            result['columns'] = df.columns.tolist()

            # Prüfe erforderliche Felder
            required_fields = ['Vorname', 'Name']  # Mindestanforderung
            has_required = any(
                any(req.lower() in col.lower() for col in result['columns'])
                for req in required_fields
            )

            if not has_required:
                result['valid'] = False
                result['errors'].append("Erforderliche Felder (Vorname, Name) nicht gefunden")

            # Zähle Zeilen
            df_full = pd.read_csv(csv_path, delimiter=delimiter)
            result['row_count'] = len(df_full)

        except Exception as e:
            result['valid'] = False
            result['errors'].append(f"CSV-Lesefehler: {str(e)}")

        return result


def import_simplimed_csv(
    db: Session,
    csv_path: str,
    user_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Convenience-Funktion für SimpliMed-Import

    Args:
        db: Datenbank-Session
        csv_path: Pfad zur CSV
        user_id: Benutzer-ID

    Returns:
        Import-Statistik
    """
    importer = SimpliMedImporter(db)
    return importer.import_from_csv(csv_path, user_id=user_id)
