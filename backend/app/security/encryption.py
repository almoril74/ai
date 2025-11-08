"""
Multi-Layer-Verschlüsselungsmodul für DSGVO-konforme Datenverschlüsselung
Implementiert AES-256 Verschlüsselung auf Feld-Ebene
"""

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend
import hashlib
import base64
from typing import Optional
import secrets

from app.core.config import settings


class EncryptionService:
    """
    Service für Multi-Layer-Verschlüsselung

    - Layer 1: Feld-Verschlüsselung (einzelne Datenfelder)
    - Layer 2: DB-Verschlüsselung (PostgreSQL pgcrypto)
    - Layer 3: Storage-Verschlüsselung (Festplatten-Verschlüsselung)
    """

    def __init__(self):
        """Initialisiert Verschlüsselungs-Service mit Keys aus Config"""
        self.master_key = settings.MASTER_ENCRYPTION_KEY.encode()
        self.field_key = settings.FIELD_ENCRYPTION_KEY.encode()

        # Fernet-Cipher für Feld-Verschlüsselung
        self.field_cipher = Fernet(self.field_key)

    def encrypt_field(self, plaintext: str) -> str:
        """
        Verschlüsselt ein einzelnes Feld

        Args:
            plaintext: Zu verschlüsselnder Text

        Returns:
            Base64-kodierter verschlüsselter Text
        """
        if not plaintext:
            return ""

        encrypted_bytes = self.field_cipher.encrypt(plaintext.encode('utf-8'))
        return base64.b64encode(encrypted_bytes).decode('utf-8')

    def decrypt_field(self, encrypted_text: str) -> str:
        """
        Entschlüsselt ein einzelnes Feld

        Args:
            encrypted_text: Base64-kodierter verschlüsselter Text

        Returns:
            Entschlüsselter Klartext
        """
        if not encrypted_text:
            return ""

        try:
            encrypted_bytes = base64.b64decode(encrypted_text.encode('utf-8'))
            decrypted_bytes = self.field_cipher.decrypt(encrypted_bytes)
            return decrypted_bytes.decode('utf-8')
        except Exception as e:
            raise ValueError(f"Entschlüsselung fehlgeschlagen: {str(e)}")

    def hash_patient_id(self, patient_id: str, salt: Optional[str] = None) -> str:
        """
        Pseudonymisierung der Patienten-ID mittels SHA-256

        Args:
            patient_id: Original Patienten-ID
            salt: Optional salt für zusätzliche Sicherheit

        Returns:
            Hexadezimaler Hash der Patienten-ID
        """
        if salt:
            data = f"{patient_id}{salt}".encode('utf-8')
        else:
            data = patient_id.encode('utf-8')

        return hashlib.sha256(data).hexdigest()

    def generate_patient_token(self, patient_id: str) -> str:
        """
        Generiert einen sicheren Token für Patienten-Links (z.B. Einwilligung)

        Args:
            patient_id: Patienten-ID

        Returns:
            Sicherer URL-sicherer Token
        """
        # Kombiniere Patient-ID mit Zufallswert
        random_data = secrets.token_bytes(16)
        combined = f"{patient_id}:{random_data.hex()}".encode('utf-8')

        # Hash mit PBKDF2 für zusätzliche Sicherheit
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.master_key[:16],  # Verwende Teil des Master-Keys als Salt
            iterations=100000,
            backend=default_backend()
        )
        key = kdf.derive(combined)

        return base64.urlsafe_b64encode(key).decode('utf-8')

    def encrypt_sensitive_data(self, data: dict) -> dict:
        """
        Verschlüsselt alle sensitiven Felder in einem Dictionary

        Args:
            data: Dictionary mit zu verschlüsselnden Daten

        Returns:
            Dictionary mit verschlüsselten Werten
        """
        sensitive_fields = [
            'vorname', 'nachname', 'geburtsdatum', 'adresse',
            'telefon', 'email', 'diagnosen', 'anamnese',
            'behandlung', 'medikation', 'notizen'
        ]

        encrypted_data = data.copy()
        for field in sensitive_fields:
            if field in encrypted_data and encrypted_data[field]:
                encrypted_data[field] = self.encrypt_field(str(encrypted_data[field]))

        return encrypted_data

    def decrypt_sensitive_data(self, encrypted_data: dict) -> dict:
        """
        Entschlüsselt alle sensitiven Felder in einem Dictionary

        Args:
            encrypted_data: Dictionary mit verschlüsselten Daten

        Returns:
            Dictionary mit entschlüsselten Werten
        """
        sensitive_fields = [
            'vorname', 'nachname', 'geburtsdatum', 'adresse',
            'telefon', 'email', 'diagnosen', 'anamnese',
            'behandlung', 'medikation', 'notizen'
        ]

        decrypted_data = encrypted_data.copy()
        for field in sensitive_fields:
            if field in decrypted_data and decrypted_data[field]:
                try:
                    decrypted_data[field] = self.decrypt_field(decrypted_data[field])
                except Exception:
                    # Bei Fehler Feld leer lassen
                    decrypted_data[field] = "[VERSCHLÜSSELUNG FEHLER]"

        return decrypted_data


class PasswordHasher:
    """Service für sicheres Passwort-Hashing mit bcrypt"""

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hasht ein Passwort mit bcrypt

        Args:
            password: Klartext-Passwort

        Returns:
            Gehashtes Passwort
        """
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verifiziert ein Passwort gegen den Hash

        Args:
            plain_password: Eingegebenes Passwort
            hashed_password: Gespeicherter Hash

        Returns:
            True wenn Passwort korrekt, sonst False
        """
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.verify(plain_password, hashed_password)


# Singleton-Instanzen
encryption_service = EncryptionService()
password_hasher = PasswordHasher()
