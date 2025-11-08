# API-Dokumentation
## DSGVO-Patientenaktensystem REST API

**Base URL:** `http://localhost:8000/api/v1`

**Interactive Docs:** `http://localhost:8000/api/v1/docs` (Swagger UI)

**ReDoc:** `http://localhost:8000/api/v1/redoc`

---

## Authentifizierung

Alle geschützten Endpoints erfordern einen JWT-Token im Authorization-Header:

```
Authorization: Bearer <access_token>
```

### POST /auth/login

Authentifiziert einen Benutzer und gibt Access & Refresh Token zurück.

**Request:**

```http
POST /api/v1/auth/login
Content-Type: multipart/form-data

username=admin&password=admin123
```

**Response (200 OK):**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "requires_mfa": false,
  "user_id": 1,
  "username": "admin",
  "role": "admin"
}
```

**Response (401 Unauthorized):**

```json
{
  "detail": "Benutzername oder Passwort falsch"
}
```

---

### GET /auth/me

Gibt Informationen über den aktuell authentifizierten Benutzer zurück.

**Request:**

```http
GET /api/v1/auth/me
Authorization: Bearer <token>
```

**Response (200 OK):**

```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@example.com",
  "full_name": "System Administrator",
  "role": "admin",
  "mfa_enabled": false,
  "is_active": true,
  "last_login": "2025-01-08T10:30:00Z"
}
```

---

### POST /auth/password/change

Ändert das Passwort des aktuellen Benutzers.

**Request:**

```http
POST /api/v1/auth/password/change
Authorization: Bearer <token>
Content-Type: application/json

{
  "old_password": "admin123",
  "new_password": "new_secure_password"
}
```

**Response (200 OK):**

```json
{
  "message": "Passwort erfolgreich geändert"
}
```

---

### POST /auth/mfa/setup

Richtet Multi-Faktor-Authentifizierung für den Benutzer ein.

**Request:**

```http
POST /api/v1/auth/mfa/setup
Authorization: Bearer <token>
```

**Response (200 OK):**

```json
{
  "secret": "JBSWY3DPEHPK3PXP",
  "qr_code": "data:image/png;base64,iVBORw0KGgoAAAANS...",
  "backup_codes": []
}
```

---

### POST /auth/mfa/verify

Verifiziert MFA-Token und aktiviert MFA.

**Request:**

```http
POST /api/v1/auth/mfa/verify
Authorization: Bearer <token>
Content-Type: application/json

{
  "token": "123456"
}
```

**Response (200 OK):**

```json
{
  "message": "MFA erfolgreich aktiviert"
}
```

---

## Patienten

### GET /patients

Listet alle aktiven Patienten auf.

**Berechtigungen:** Alle authentifizierten Benutzer

**Request:**

```http
GET /api/v1/patients?skip=0&limit=100
Authorization: Bearer <token>
```

**Query Parameters:**

| Parameter | Typ | Default | Beschreibung |
|-----------|-----|---------|--------------|
| skip | int | 0 | Anzahl zu überspringender Einträge |
| limit | int | 100 | Max. Anzahl zurückzugebender Einträge |

**Response (200 OK):**

```json
[
  {
    "id": 1,
    "pseudonym_id": "a3f5e8d2...",
    "vorname": "Max",
    "nachname": "Mustermann",
    "geburtsdatum": "1980-05-15",
    "is_active": true,
    "last_accessed_at": "2025-01-08T10:00:00Z"
  }
]
```

---

### GET /patients/{patient_id}

Ruft Details eines einzelnen Patienten ab (entschlüsselt).

**Berechtigungen:** Alle authentifizierten Benutzer

**Audit-Logging:** Dieser Zugriff wird protokolliert!

**Request:**

```http
GET /api/v1/patients/1
Authorization: Bearer <token>
```

**Response (200 OK):**

```json
{
  "id": 1,
  "pseudonym_id": "a3f5e8d2...",
  "vorname": "Max",
  "nachname": "Mustermann",
  "geburtsdatum": "1980-05-15",
  "adresse": "Musterstraße 123, 12345 Musterstadt",
  "telefon": "+49 123 456789",
  "email": "max@example.com",
  "anamnese": "Rückenschmerzen seit 2 Wochen",
  "allergien": "Keine bekannt",
  "medikation": "Ibuprofen 400mg bei Bedarf",
  "vorerkrankungen": "Keine",
  "is_active": true,
  "consent_given": true,
  "consent_date": "2025-01-01T10:00:00Z",
  "imported_from_simplimed": false,
  "created_at": "2025-01-01T10:00:00Z",
  "updated_at": "2025-01-08T10:00:00Z"
}
```

**Response (404 Not Found):**

```json
{
  "detail": "Patient nicht gefunden"
}
```

---

### POST /patients

Erstellt einen neuen Patienten.

**Berechtigungen:** Mindestens Rolle "assistant"

**Request:**

```http
POST /api/v1/patients
Authorization: Bearer <token>
Content-Type: application/json

{
  "vorname": "Anna",
  "nachname": "Schmidt",
  "geburtsdatum": "1990-03-20",
  "adresse": "Teststraße 45, 54321 Teststadt",
  "telefon": "+49 987 654321",
  "email": "anna@example.com",
  "anamnese": "Kopfschmerzen",
  "allergien": null,
  "medikation": null,
  "vorerkrankungen": null,
  "consent_given": true
}
```

**Response (201 Created):**

```json
{
  "id": 2,
  "pseudonym_id": "b4g6f9e3...",
  "vorname": "Anna",
  "nachname": "Schmidt",
  ...
}
```

**Response (400 Bad Request):**

```json
{
  "detail": "Patient existiert bereits"
}
```

---

### PUT /patients/{patient_id}

Aktualisiert Patientendaten.

**Berechtigungen:** Mindestens Rolle "assistant"

**Request:**

```http
PUT /api/v1/patients/2
Authorization: Bearer <token>
Content-Type: application/json

{
  "telefon": "+49 111 222333",
  "anamnese": "Kopfschmerzen, verbessert"
}
```

**Response (200 OK):**

```json
{
  "id": 2,
  "pseudonym_id": "b4g6f9e3...",
  "vorname": "Anna",
  "nachname": "Schmidt",
  "telefon": "+49 111 222333",
  ...
}
```

---

### DELETE /patients/{patient_id}

Löscht einen Patienten (Soft Delete).

**Berechtigungen:** Mindestens Rolle "doctor"

**Request:**

```http
DELETE /api/v1/patients/2
Authorization: Bearer <token>
```

**Response (204 No Content):**

```
(Leer)
```

---

## Rollen & Berechtigungen

| Rolle | Beschreibung | Berechtigungen |
|-------|--------------|----------------|
| **admin** | Administrator | Volle Rechte |
| **doctor** | Osteopath/Behandler | Patienten CRUD, Behandlungen CRUD |
| **assistant** | Praxisassistent | Patienten Create/Update, Behandlungen Read |
| **readonly** | Nur Lesezugriff | Patienten Read |

---

## Fehler-Codes

| Status Code | Bedeutung |
|-------------|-----------|
| 200 | OK - Request erfolgreich |
| 201 | Created - Ressource erstellt |
| 204 | No Content - Erfolgreich, keine Daten zurück |
| 400 | Bad Request - Validierungsfehler |
| 401 | Unauthorized - Nicht authentifiziert |
| 403 | Forbidden - Keine Berechtigung |
| 404 | Not Found - Ressource nicht gefunden |
| 422 | Unprocessable Entity - Ungültige Eingabedaten |
| 500 | Internal Server Error - Serverfehler |

---

## Rate Limiting

Aktuell kein Rate Limiting implementiert.

**Empfohlen für Produktion:**
- 100 Requests pro Minute pro IP
- 1000 Requests pro Stunde pro Benutzer

---

## Verschlüsselung

**Alle sensiblen Daten werden automatisch verschlüsselt:**

- Verschlüsselte Felder:
  - `vorname`, `nachname`, `geburtsdatum`
  - `adresse`, `telefon`, `email`
  - `anamnese`, `allergien`, `medikation`, `vorerkrankungen`

- Verschlüsselung: AES-256
- Pseudonymisierung: SHA-256 für Patienten-IDs

**Die API gibt automatisch entschlüsselte Daten zurück, wenn der Benutzer berechtigt ist.**

---

## Audit-Logging

**Alle Zugriffe auf Patientendaten werden protokolliert:**

Protokollierte Informationen:
- Benutzer-ID
- Aktion (read, create, update, delete)
- Zeitstempel
- IP-Adresse
- Ressourcen-ID (Patient-ID)

**Logs werden gespeichert in:**
- Datei: `/var/log/patientenakte/audit.log`
- Datenbank: Tabelle `audit_logs`

**Retention:** 2 Jahre

---

## Beispiel-Client (Python)

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Login
response = requests.post(
    f"{BASE_URL}/auth/login",
    data={"username": "admin", "password": "admin123"}
)
token = response.json()["access_token"]

# Headers mit Token
headers = {"Authorization": f"Bearer {token}"}

# Patienten abrufen
patients = requests.get(f"{BASE_URL}/patients", headers=headers).json()

# Patient erstellen
new_patient = {
    "vorname": "Test",
    "nachname": "Patient",
    "geburtsdatum": "2000-01-01",
    "consent_given": True
}
response = requests.post(
    f"{BASE_URL}/patients",
    headers=headers,
    json=new_patient
)
patient_id = response.json()["id"]

# Patient abrufen
patient = requests.get(
    f"{BASE_URL}/patients/{patient_id}",
    headers=headers
).json()
```

---

## Beispiel-Client (JavaScript/TypeScript)

```typescript
const BASE_URL = 'http://localhost:8000/api/v1';

// Login
const loginResponse = await fetch(`${BASE_URL}/auth/login`, {
  method: 'POST',
  headers: { 'Content-Type': 'multipart/form-data' },
  body: new URLSearchParams({
    username: 'admin',
    password: 'admin123'
  })
});
const { access_token } = await loginResponse.json();

// Patienten abrufen
const patientsResponse = await fetch(`${BASE_URL}/patients`, {
  headers: { 'Authorization': `Bearer ${access_token}` }
});
const patients = await patientsResponse.json();

// Patient erstellen
const newPatient = {
  vorname: 'Test',
  nachname: 'Patient',
  geburtsdatum: '2000-01-01',
  consent_given: true
};
const createResponse = await fetch(`${BASE_URL}/patients`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${access_token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(newPatient)
});
const patient = await createResponse.json();
```

---

## Support

Bei Fragen zur API:
- Interactive Docs: `http://localhost:8000/api/v1/docs`
- E-Mail: support@example.com
- GitHub Issues: [Repository-URL]/issues
