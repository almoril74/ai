"""Authentication Schemas"""

from pydantic import BaseModel, EmailStr
from typing import Optional


class LoginRequest(BaseModel):
    """Login-Request"""
    username: str
    password: str
    mfa_token: Optional[str] = None


class LoginResponse(BaseModel):
    """Login-Response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    requires_mfa: bool = False
    user_id: int
    username: str
    role: str


class TokenResponse(BaseModel):
    """Token-Response"""
    access_token: str
    token_type: str = "bearer"


class MFASetupResponse(BaseModel):
    """MFA-Setup-Response"""
    secret: str
    qr_code: str  # Base64-encoded QR code
    backup_codes: list[str]


class MFAVerifyRequest(BaseModel):
    """MFA-Verification-Request"""
    token: str


class PasswordChangeRequest(BaseModel):
    """Passwort-Änderungs-Request"""
    old_password: str
    new_password: str
