#!/bin/bash

# DSGVO-Patientenaktensystem - Setup-Skript
# Initialisiert das System für Entwicklung und Produktion

set -e  # Exit bei Fehler

echo "======================================"
echo " DSGVO-Patientenaktensystem Setup"
echo "======================================"
echo ""

# Farben
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Funktion für erfolgreiche Schritte
success() {
    echo -e "${GREEN}✓${NC} $1"
}

# Funktion für Warnungen
warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Funktion für Fehler
error() {
    echo -e "${RED}✗${NC} $1"
}

# Prüfe ob .env existiert
if [ ! -f .env ]; then
    echo "Erstelle .env aus .env.example..."
    cp .env.example .env
    warning ".env-Datei erstellt - BITTE WERTE ANPASSEN!"
    echo ""
    echo "Wichtig: Folgende Werte MÜSSEN angepasst werden:"
    echo "  - MASTER_ENCRYPTION_KEY"
    echo "  - FIELD_ENCRYPTION_KEY"
    echo "  - SECRET_KEY"
    echo "  - DATABASE_URL"
    echo ""
    read -p "Drücke Enter wenn .env angepasst wurde..."
else
    success ".env-Datei existiert bereits"
fi

# Backend Setup
echo ""
echo "=== Backend Setup ==="

if [ ! -d "backend/venv" ]; then
    echo "Erstelle Python Virtual Environment..."
    cd backend
    python3 -m venv venv
    success "Virtual Environment erstellt"
else
    cd backend
    success "Virtual Environment existiert bereits"
fi

echo "Aktiviere Virtual Environment und installiere Dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
success "Python-Dependencies installiert"

# Generiere Encryption Keys
echo ""
echo "Generiere Verschlüsselungs-Keys..."
python3 << END
from cryptography.fernet import Fernet
print("MASTER_ENCRYPTION_KEY=" + Fernet.generate_key().decode())
print("FIELD_ENCRYPTION_KEY=" + Fernet.generate_key().decode())
END

echo ""
warning "Kopiere die Keys oben in deine .env-Datei!"

# Datenbank Setup
echo ""
echo "=== Datenbank Setup ==="
read -p "Datenbank initialisieren? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Erstelle Datenbank-Tabellen..."
    alembic upgrade head
    success "Datenbank initialisiert"

    echo ""
    read -p "Admin-Benutzer erstellen? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python scripts/create_admin.py
        success "Admin-Benutzer erstellt"
    fi
fi

cd ..

# Frontend Setup
echo ""
echo "=== Frontend Setup ==="

if [ ! -d "frontend/node_modules" ]; then
    cd frontend
    echo "Installiere Node-Dependencies..."
    npm install
    success "Node-Dependencies installiert"
    cd ..
else
    success "Node-Dependencies bereits installiert"
fi

# Docker Setup
echo ""
echo "=== Docker Setup (optional) ==="
read -p "Docker-Container starten? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Starte Docker-Container..."
    docker-compose up -d
    success "Docker-Container gestartet"

    echo "Warte auf Datenbank..."
    sleep 5

    echo "Führe Datenbank-Migrationen aus..."
    docker-compose exec backend alembic upgrade head
    success "Migrationen abgeschlossen"
fi

# Abschluss
echo ""
echo "======================================"
echo " Setup abgeschlossen!"
echo "======================================"
echo ""
echo "Nächste Schritte:"
echo ""
echo "1. Backend starten:"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   uvicorn app.main:app --reload"
echo ""
echo "2. Frontend starten (neues Terminal):"
echo "   cd frontend"
echo "   npm run dev"
echo ""
echo "3. System aufrufen:"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/api/v1/docs"
echo "   Frontend: http://localhost:3000"
echo ""
echo "4. Login mit:"
echo "   Username: admin"
echo "   Password: admin123"
echo "   ${RED}WICHTIG: Passwort sofort ändern!${NC}"
echo ""
echo "======================================"

success "System ist einsatzbereit!"
