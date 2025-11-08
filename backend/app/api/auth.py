"""
Authentifizierungs-Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.auth import (
    LoginResponse, MFASetupResponse, MFAVerifyRequest,
    PasswordChangeRequest, TokenResponse
)
from app.security.authentication import (
    auth_service, get_current_active_user
)
from app.security.audit import audit_logger, AuditAction
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=LoginResponse)
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Login-Endpoint mit MFA-Support

    Returns:
        Access Token und Refresh Token
    """
    # Client IP für Audit-Log
    client_ip = request.client.host if request.client else "unknown"

    # Benutzer authentifizieren
    user = auth_service.authenticate_user(
        db=db,
        username=form_data.username,
        password=form_data.password,
        ip_address=client_ip
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Benutzername oder Passwort falsch",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Prüfe MFA wenn aktiviert
    if user.mfa_enabled:
        # TODO: MFA-Token aus separatem Feld holen
        # Für jetzt: Login erfolgreich, aber MFA erforderlich
        audit_logger.log_authentication(
            username=user.username,
            action=AuditAction.LOGIN,
            ip_address=client_ip,
            success=True
        )

        # Temporärer Token (nur für MFA-Verifizierung)
        temp_token = auth_service.create_access_token(
            data={"sub": str(user.id), "mfa_pending": True}
        )

        return LoginResponse(
            access_token=temp_token,
            refresh_token="",
            requires_mfa=True,
            user_id=user.id,
            username=user.username,
            role=user.role.value
        )

    # Erstelle Tokens
    access_token = auth_service.create_access_token(
        data={"sub": str(user.id)}
    )
    refresh_token = auth_service.create_refresh_token(user.id)

    # Log erfolgreichen Login
    audit_logger.log_authentication(
        username=user.username,
        action=AuditAction.LOGIN,
        ip_address=client_ip,
        success=True
    )

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        requires_mfa=False,
        user_id=user.id,
        username=user.username,
        role=user.role.value
    )


@router.post("/mfa/setup", response_model=MFASetupResponse)
async def setup_mfa(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Richtet MFA für Benutzer ein

    Returns:
        MFA-Secret und QR-Code
    """
    if current_user.mfa_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA bereits aktiviert"
        )

    # Generiere MFA-Secret
    secret = auth_service.generate_mfa_secret()
    qr_code = auth_service.get_mfa_qr_code(current_user.username, secret)

    # Speichere Secret (wird erst bei Verifizierung aktiviert)
    current_user.mfa_secret = secret
    db.commit()

    # Generiere Backup-Codes (TODO: Implementieren)
    backup_codes = []  # In Produktion: echte Backup-Codes generieren

    return MFASetupResponse(
        secret=secret,
        qr_code=qr_code,
        backup_codes=backup_codes
    )


@router.post("/mfa/verify")
async def verify_mfa(
    mfa_data: MFAVerifyRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Verifiziert MFA-Token und aktiviert MFA

    Args:
        mfa_data: MFA-Token

    Returns:
        Success-Status
    """
    if not current_user.mfa_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA nicht eingerichtet"
        )

    # Verifiziere Token
    if not auth_service.verify_mfa_token(current_user.mfa_secret, mfa_data.token):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ungültiger MFA-Token"
        )

    # Aktiviere MFA
    current_user.mfa_enabled = True
    db.commit()

    # Audit-Log
    audit_logger.log_event(
        user_id=current_user.id,
        action=AuditAction.MFA_ENABLED,
        success=True
    )

    return {"message": "MFA erfolgreich aktiviert"}


@router.post("/password/change")
async def change_password(
    password_data: PasswordChangeRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Ändert Passwort des aktuellen Benutzers

    Args:
        password_data: Altes und neues Passwort

    Returns:
        Success-Status
    """
    from app.security.encryption import password_hasher

    # Verifiziere altes Passwort
    if not password_hasher.verify_password(
        password_data.old_password,
        current_user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Altes Passwort falsch"
        )

    # Setze neues Passwort
    current_user.hashed_password = password_hasher.hash_password(
        password_data.new_password
    )
    current_user.password_changed_at = db.func.now()
    db.commit()

    # Audit-Log
    audit_logger.log_event(
        user_id=current_user.id,
        action=AuditAction.PASSWORD_CHANGED,
        success=True
    )

    return {"message": "Passwort erfolgreich geändert"}


@router.get("/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Gibt Informationen über aktuellen Benutzer zurück

    Returns:
        Benutzer-Informationen
    """
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role.value,
        "mfa_enabled": current_user.mfa_enabled,
        "is_active": current_user.is_active,
        "last_login": current_user.last_login
    }
