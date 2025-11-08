#!/usr/bin/env python3
"""
Initialisiert die Datenbank und erstellt einen Admin-Benutzer
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.core.database import engine, Base
from app.core.database import SessionLocal
from app.models.user import User, UserRole
from app.models.patient import Patient
from app.models.treatment import Treatment
from app.models.consent import Consent
from app.models.audit_log import AuditLog
from app.security.encryption import password_hasher

print("🔧 Initialisiere Datenbank...")

# Erstelle alle Tabellen
Base.metadata.create_all(bind=engine)
print("✅ Tabellen erstellt")

# Erstelle Admin-Benutzer
db = SessionLocal()

try:
    # Prüfe ob Admin bereits existiert
    existing = db.query(User).filter(User.username == "admin").first()
    if existing:
        print("ℹ️  Admin-Benutzer existiert bereits")
    else:
        # Erstelle Admin
        admin = User(
            username="admin",
            email="admin@example.com",
            full_name="System Administrator",
            hashed_password=password_hasher.hash_password("admin123"),
            role=UserRole.ADMIN,
            is_active=True,
            is_superuser=True,
            mfa_enabled=False
        )

        db.add(admin)
        db.commit()

        print("✅ Admin-Benutzer erstellt:")
        print("   Username: admin")
        print("   Password: admin123")
        print("   ⚠️  BITTE PASSWORT SOFORT ÄNDERN!")

except Exception as e:
    print(f"❌ Fehler: {e}")
    db.rollback()
finally:
    db.close()

print("\n✅ Datenbank-Setup abgeschlossen!")
