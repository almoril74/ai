# DSGVO-Konformes Patientenaktensystem für Osteopathiepraxis

Ein vollständig DSGVO-konformes digitales Patientenaktensystem mit SimpliMed-Integration.

## 🔐 Sicherheit & Compliance

- **DSGVO-konform**: Art. 9 DSGVO (Gesundheitsdaten)
- **Verschlüsselung**: Multi-Layer AES-256-Verschlüsselung
- **Audit-Logging**: Vollständige Nachverfolgbarkeit aller Zugriffe
- **Berufsgeheimnis**: § 203 StGB-konform
- **Aufbewahrungsfristen**: 10 Jahre gem. § 630f BGB

## 🏗️ Architektur

```
┌─────────────────┐
│   Frontend      │ React + TypeScript + TLS 1.3
└────────┬────────┘
         │
┌────────▼────────┐
│   API Gateway   │ nginx + MFA
└────────┬────────┘
         │
┌────────▼────────┐
│  FastAPI        │ Python Backend
│  Application    │ - Geschäftslogik
│                 │ - Verschlüsselung
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼──┐  ┌──▼────────┐
│  DB  │  │ SimpliMed │
│(Enc.)│  │ Interface │
└──────┘  └───────────┘
```

## 📋 Features

### Kernsystem
- ✅ Multi-Faktor-Authentifizierung (MFA)
- ✅ Rollenbasierte Zugriffskontrolle (RBAC)
- ✅ Ende-zu-Ende-Verschlüsselung
- ✅ Audit-Logging für alle Datenzugriffe
- ✅ Automatische Backup-Verschlüsselung
- ✅ Session-Management mit Auto-Timeout

### Datenschutz
- ✅ Pseudonymisierung von Patienten-IDs
- ✅ Feld-Level-Verschlüsselung
- ✅ Einwilligungsverwaltung
- ✅ Widerrufsmöglichkeit
- ✅ Löschkonzept nach Aufbewahrungsfristen
- ✅ Datenschutz-Folgenabschätzung (DSFA)

### SimpliMed-Integration
- ✅ CSV-Import mit Verschlüsselung
- ✅ Daten-Mapping und -Validierung
- ✅ Automatische Pseudonymisierung

## 🚀 Schnellstart

### Voraussetzungen
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Docker & Docker Compose (optional)

### Installation

```bash
# Repository klonen
git clone <repository-url>
cd ai

# Backend Setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Umgebungsvariablen konfigurieren
cp .env.example .env
# .env bearbeiten mit eigenen Werten

# Datenbank initialisieren
alembic upgrade head

# Backend starten
uvicorn app.main:app --reload

# Frontend Setup (in neuem Terminal)
cd frontend
npm install
npm run dev
```

### Docker-Deployment

```bash
# Alle Services starten
docker-compose up -d

# Services stoppen
docker-compose down

# Logs anzeigen
docker-compose logs -f
```

## 📁 Projektstruktur

```
.
├── backend/                # FastAPI Backend
│   ├── app/
│   │   ├── api/           # API Endpoints
│   │   ├── core/          # Konfiguration & Sicherheit
│   │   ├── models/        # Datenbank-Modelle
│   │   ├── schemas/       # Pydantic Schemas
│   │   ├── services/      # Business Logic
│   │   ├── security/      # Verschlüsselung & Audit
│   │   └── main.py        # Haupt-Anwendung
│   ├── alembic/           # Datenbank-Migrationen
│   ├── tests/             # Unit & Integration Tests
│   └── requirements.txt
│
├── frontend/              # React Frontend
│   ├── src/
│   │   ├── components/    # React Components
│   │   ├── pages/         # Seiten
│   │   ├── hooks/         # Custom Hooks
│   │   ├── services/      # API Services
│   │   └── utils/         # Utilities
│   ├── public/
│   └── package.json
│
├── docs/                  # Dokumentation
│   ├── DSGVO/            # DSGVO-Dokumentation
│   ├── API.md            # API-Dokumentation
│   └── DEPLOYMENT.md     # Deployment-Anleitung
│
├── docker-compose.yml
├── .env.example
└── README.md
```

## 🔧 Konfiguration

### Umgebungsvariablen (.env)

```env
# Datenbank
DATABASE_URL=postgresql://user:password@localhost:5432/patientenakte

# Verschlüsselung
MASTER_ENCRYPTION_KEY=<32-byte-key>
FIELD_ENCRYPTION_KEY=<32-byte-key>

# JWT
SECRET_KEY=<random-secret>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Sicherheit
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ORIGINS=http://localhost:3000

# SimpliMed
SIMPLIMED_IMPORT_PATH=/path/to/simplimed/export
```

## 📊 Datenbank-Schema

- **users**: Benutzer mit MFA und Rollen
- **patients**: Verschlüsselte Patientendaten
- **treatments**: Behandlungsdokumentation
- **consents**: Einwilligungsverwaltung
- **audit_logs**: Vollständige Zugriffsprotokolle

## 🧪 Tests

```bash
# Backend Tests
cd backend
pytest

# Frontend Tests
cd frontend
npm test

# E2E Tests
npm run test:e2e
```

## 📄 Lizenz

Proprietary - Alle Rechte vorbehalten

## 🤝 Support

Bei Fragen oder Problemen:
- Dokumentation: `docs/`
- Issues: GitHub Issues

## ⚠️ Wichtige Hinweise

- **Produktivbetrieb**: Vor Produktivbetrieb DSFA durchführen
- **Backups**: Tägliche verschlüsselte Backups einrichten
- **Monitoring**: Audit-Logs regelmäßig überprüfen
- **Updates**: Sicherheitsupdates zeitnah einspielen
- **Schulung**: Personal in Datenschutz schulen

## 📚 Gesetzliche Grundlagen

- DSGVO Art. 9 (Gesundheitsdaten)
- § 203 StGB (Berufsgeheimnis)
- § 630f BGB (Dokumentationspflicht)
- Patientenrechtegesetz (PatRG)
- Landesheilberufegesetze
