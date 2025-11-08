"""
Skript zum Erstellen eines Admin-Benutzers
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.core.database import SessionLocal
from app.models.user import User, UserRole
from app.security.encryption import password_hasher


def create_admin_user(
    username: str = "admin",
    password: str = "admin123",
    email: str = "admin@example.com",
    full_name: str = "System Administrator"
):
    """
    Erstellt Admin-Benutzer

    Args:
        username: Benutzername
        password: Passwort (BITTE IN PRODUKTION ÄNDERN!)
        email: E-Mail
        full_name: Voller Name
    """
    db = SessionLocal()

    try:
        # Prüfe ob Admin bereits existiert
        existing = db.query(User).filter(User.username == username).first()
        if existing:
            print(f"❌ Benutzer '{username}' existiert bereits!")
            return

        # Erstelle Admin
        admin = User(
            username=username,
            email=email,
            full_name=full_name,
            hashed_password=password_hasher.hash_password(password),
            role=UserRole.ADMIN,
            is_active=True,
            is_superuser=True,
            mfa_enabled=False
        )

        db.add(admin)
        db.commit()

        print(f"✅ Admin-Benutzer '{username}' erfolgreich erstellt!")
        print(f"   E-Mail: {email}")
        print(f"   Passwort: {password}")
        print(f"   ⚠️  BITTE PASSWORT SOFORT ÄNDERN!")

    except Exception as e:
        print(f"❌ Fehler beim Erstellen des Admin-Benutzers: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_admin_user()
