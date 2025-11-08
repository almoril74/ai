"""
JWT-basiertes Authentifizierungssystem mit MFA-Support
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import pyotp
import qrcode
import io
import base64

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.security.encryption import password_hasher
from app.security.audit import audit_logger, AuditAction

# OAuth2 Schema
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/login")


class AuthenticationService:
    """Service für Authentifizierung und Autorisierung"""

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        Erstellt JWT Access Token

        Args:
            data: Daten für Token-Payload
            expires_delta: Gültigkeitsdauer

        Returns:
            JWT Token
        """
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({"exp": expire, "iat": datetime.utcnow()})

        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )

        return encoded_jwt

    @staticmethod
    def create_refresh_token(user_id: int) -> str:
        """
        Erstellt Refresh Token

        Args:
            user_id: Benutzer-ID

        Returns:
            Refresh Token
        """
        expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        data = {"sub": str(user_id), "type": "refresh"}
        return AuthenticationService.create_access_token(data, expires_delta)

    @staticmethod
    def verify_token(token: str) -> dict:
        """
        Verifiziert JWT Token

        Args:
            token: JWT Token

        Returns:
            Decoded Token-Payload

        Raises:
            HTTPException: Bei ungültigem Token
        """
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token ungültig oder abgelaufen",
                headers={"WWW-Authenticate": "Bearer"},
            )

    @staticmethod
    def authenticate_user(db: Session, username: str, password: str, ip_address: str = None) -> Optional[User]:
        """
        Authentifiziert Benutzer mit Username und Passwort

        Args:
            db: Datenbank-Session
            username: Benutzername
            password: Passwort
            ip_address: Client IP-Adresse für Audit-Log

        Returns:
            User-Objekt oder None bei Fehler
        """
        user = db.query(User).filter(User.username == username).first()

        if not user:
            # Log fehlgeschlagenen Login
            audit_logger.log_authentication(
                username=username,
                action=AuditAction.LOGIN_FAILED,
                ip_address=ip_address,
                success=False,
                error_message="Benutzer nicht gefunden"
            )
            return None

        # Prüfe ob Account gesperrt
        if user.is_locked:
            audit_logger.log_authentication(
                username=username,
                action=AuditAction.LOGIN_FAILED,
                ip_address=ip_address,
                success=False,
                error_message="Account gesperrt"
            )
            return None

        # Prüfe ob Account aktiv
        if not user.is_active:
            audit_logger.log_authentication(
                username=username,
                action=AuditAction.LOGIN_FAILED,
                ip_address=ip_address,
                success=False,
                error_message="Account deaktiviert"
            )
            return None

        # Verifiziere Passwort
        if not password_hasher.verify_password(password, user.hashed_password):
            # Fehlversuch zählen
            user.failed_login_attempts += 1

            # Sperre nach zu vielen Versuchen
            if user.failed_login_attempts >= settings.MAX_LOGIN_ATTEMPTS:
                user.locked_until = datetime.utcnow() + timedelta(minutes=settings.LOGIN_TIMEOUT_MINUTES)

            db.commit()

            audit_logger.log_authentication(
                username=username,
                action=AuditAction.LOGIN_FAILED,
                ip_address=ip_address,
                success=False,
                error_message="Falsches Passwort"
            )
            return None

        # Erfolgreicher Login - Reset Fehlversuche
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login = datetime.utcnow()
        db.commit()

        return user

    @staticmethod
    def generate_mfa_secret() -> str:
        """
        Generiert MFA-Secret für TOTP

        Returns:
            Base32-kodiertes Secret
        """
        return pyotp.random_base32()

    @staticmethod
    def get_mfa_qr_code(username: str, secret: str) -> str:
        """
        Generiert QR-Code für MFA-Einrichtung

        Args:
            username: Benutzername
            secret: MFA-Secret

        Returns:
            Base64-kodiertes QR-Code-Bild
        """
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=username,
            issuer_name=settings.MFA_ISSUER_NAME
        )

        # QR-Code generieren
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        # In Base64 konvertieren
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)

        return base64.b64encode(buffer.getvalue()).decode()

    @staticmethod
    def verify_mfa_token(secret: str, token: str) -> bool:
        """
        Verifiziert MFA-Token

        Args:
            secret: MFA-Secret
            token: 6-stelliger TOTP-Code

        Returns:
            True wenn Token gültig
        """
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=1)  # 30s Toleranz


# Dependency für geschützte Endpoints
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency: Holt aktuellen authentifizierten Benutzer

    Args:
        token: JWT Token
        db: Datenbank-Session

    Returns:
        User-Objekt

    Raises:
        HTTPException: Bei ungültigem Token oder Benutzer nicht gefunden
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentifizierung fehlgeschlagen",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Token verifizieren
    payload = AuthenticationService.verify_token(token)
    user_id: str = payload.get("sub")

    if user_id is None:
        raise credentials_exception

    # Benutzer aus DB laden
    user = db.query(User).filter(User.id == int(user_id)).first()

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account deaktiviert"
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency: Stellt sicher dass Benutzer aktiv ist

    Args:
        current_user: Aktueller Benutzer

    Returns:
        User-Objekt

    Raises:
        HTTPException: Wenn Benutzer nicht aktiv
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inaktiver Benutzer"
        )
    return current_user


def require_role(required_role):
    """
    Decorator Factory: Erfordert bestimmte Benutzerrolle

    Args:
        required_role: Erforderliche Rolle (UserRole)

    Returns:
        Dependency-Funktion
    """
    async def role_checker(current_user: User = Depends(get_current_active_user)):
        if not current_user.has_permission(required_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Keine Berechtigung für diese Aktion"
            )
        return current_user

    return role_checker


# Service-Instanz
auth_service = AuthenticationService()
