"""
DSGVO-konformes Audit-Logging-System
Protokolliert alle Zugriffe auf Patientendaten gem. Art. 32 DSGVO
"""

from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum
import json
import structlog
from pathlib import Path

from app.core.config import settings


class AuditAction(str, Enum):
    """Typen von Audit-Events"""
    # Authentifizierung
    LOGIN = "login"
    LOGOUT = "logout"
    LOGIN_FAILED = "login_failed"
    MFA_ENABLED = "mfa_enabled"
    MFA_DISABLED = "mfa_disabled"
    PASSWORD_CHANGED = "password_changed"

    # Datenzugriff
    READ = "read"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    EXPORT = "export"

    # Patientendaten
    PATIENT_VIEWED = "patient_viewed"
    PATIENT_CREATED = "patient_created"
    PATIENT_UPDATED = "patient_updated"
    PATIENT_DELETED = "patient_deleted"

    # Behandlungen
    TREATMENT_VIEWED = "treatment_viewed"
    TREATMENT_CREATED = "treatment_created"
    TREATMENT_UPDATED = "treatment_updated"
    TREATMENT_DELETED = "treatment_deleted"

    # Einwilligungen
    CONSENT_GIVEN = "consent_given"
    CONSENT_REVOKED = "consent_revoked"
    CONSENT_VIEWED = "consent_viewed"

    # Datenimport/-export
    SIMPLIMED_IMPORT = "simplimed_import"
    DATA_EXPORT = "data_export"
    BACKUP_CREATED = "backup_created"

    # System
    SYSTEM_CONFIG_CHANGED = "system_config_changed"
    USER_CREATED = "user_created"
    USER_DELETED = "user_deleted"
    PERMISSION_CHANGED = "permission_changed"


class AuditLogger:
    """
    Zentrale Audit-Logging-Klasse für DSGVO-Compliance

    Protokolliert:
    - Wer (user_id)
    - Was (action)
    - Wann (timestamp)
    - Auf welche Daten (resource_id, resource_type)
    - Von wo (ip_address)
    - Ergebnis (success, error_message)
    """

    def __init__(self):
        """Initialisiert Audit-Logger mit strukturiertem Logging"""
        # Stelle sicher dass Log-Verzeichnis existiert
        log_file = Path(settings.AUDIT_LOG_FILE)
        log_file.parent.mkdir(parents=True, exist_ok=True)

        # Konfiguriere structlog für strukturiertes JSON-Logging
        structlog.configure(
            processors=[
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.JSONRenderer()
            ],
            wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
            context_class=dict,
            logger_factory=structlog.PrintLoggerFactory(),
        )

        self.logger = structlog.get_logger()

    def log_event(
        self,
        user_id: Optional[int],
        action: AuditAction,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Protokolliert ein Audit-Event

        Args:
            user_id: ID des Benutzers der die Aktion durchführt
            action: Art der durchgeführten Aktion
            resource_type: Typ der betroffenen Ressource (z.B. "patient", "treatment")
            resource_id: ID der betroffenen Ressource
            ip_address: IP-Adresse des Clients
            user_agent: Browser/Client User-Agent
            success: Ob die Aktion erfolgreich war
            error_message: Fehlermeldung bei Misserfolg
            additional_data: Zusätzliche Daten für das Log
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "action": action.value,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "success": success,
            "error_message": error_message
        }

        # Füge zusätzliche Daten hinzu
        if additional_data:
            log_entry["additional_data"] = additional_data

        # Schreibe in strukturiertes Log
        if success:
            self.logger.info("audit_event", **log_entry)
        else:
            self.logger.warning("audit_event_failed", **log_entry)

        # Zusätzlich in dedizierte Audit-Log-Datei
        self._write_to_audit_file(log_entry)

    def _write_to_audit_file(self, log_entry: Dict[str, Any]) -> None:
        """
        Schreibt Audit-Event in dedizierte Audit-Log-Datei

        Args:
            log_entry: Log-Eintrag als Dictionary
        """
        try:
            with open(settings.AUDIT_LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        except Exception as e:
            # Fallback auf stderr wenn File-Schreibvorgang fehlschlägt
            print(f"AUDIT LOG FEHLER: {e}", file=sys.stderr)

    def log_patient_access(
        self,
        user_id: int,
        patient_id: str,
        action: AuditAction,
        ip_address: str,
        success: bool = True,
        details: Optional[str] = None
    ) -> None:
        """
        Spezialisierte Methode für Patienten-Zugriffe

        Args:
            user_id: ID des zugreifenden Benutzers
            patient_id: ID des Patienten
            action: Art des Zugriffs
            ip_address: IP-Adresse
            success: Erfolg der Aktion
            details: Zusätzliche Details
        """
        self.log_event(
            user_id=user_id,
            action=action,
            resource_type="patient",
            resource_id=patient_id,
            ip_address=ip_address,
            success=success,
            additional_data={"details": details} if details else None
        )

    def log_authentication(
        self,
        username: str,
        action: AuditAction,
        ip_address: str,
        success: bool,
        error_message: Optional[str] = None
    ) -> None:
        """
        Spezialisierte Methode für Authentifizierungs-Events

        Args:
            username: Benutzername
            action: Authentifizierungs-Aktion
            ip_address: IP-Adresse
            success: Erfolg der Authentifizierung
            error_message: Fehlermeldung bei Misserfolg
        """
        self.log_event(
            user_id=None,  # Noch nicht authentifiziert
            action=action,
            resource_type="authentication",
            resource_id=username,
            ip_address=ip_address,
            success=success,
            error_message=error_message
        )

    def get_patient_access_log(
        self,
        patient_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> list:
        """
        Ruft alle Zugriffe auf einen bestimmten Patienten ab
        DSGVO Art. 15 - Auskunftsrecht

        Args:
            patient_id: ID des Patienten
            start_date: Start-Datum für Filter
            end_date: End-Datum für Filter

        Returns:
            Liste aller Zugriffe auf diesen Patienten
        """
        access_log = []

        try:
            with open(settings.AUDIT_LOG_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        entry = json.loads(line)

                        # Filter nach Patient-ID
                        if entry.get('resource_id') != patient_id:
                            continue

                        # Filter nach Datum
                        entry_date = datetime.fromisoformat(entry['timestamp'])
                        if start_date and entry_date < start_date:
                            continue
                        if end_date and entry_date > end_date:
                            continue

                        access_log.append(entry)
                    except json.JSONDecodeError:
                        continue
        except FileNotFoundError:
            pass

        return access_log


# Singleton-Instanz
import sys
audit_logger = AuditLogger()
