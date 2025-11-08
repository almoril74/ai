# Deployment-Anleitung
## DSGVO-Patientenaktensystem

---

## Inhaltsverzeichnis

1. [Systemanforderungen](#systemanforderungen)
2. [Schnellstart (Entwicklung)](#schnellstart-entwicklung)
3. [Produktions-Deployment](#produktions-deployment)
4. [Docker-Deployment](#docker-deployment)
5. [Sicherheits-Checkliste](#sicherheits-checkliste)
6. [Backup & Recovery](#backup--recovery)
7. [Monitoring](#monitoring)

---

## Systemanforderungen

### Minimum (Entwicklung)
- **CPU:** 2 Kerne
- **RAM:** 4 GB
- **Storage:** 20 GB SSD
- **OS:** Ubuntu 20.04+, Debian 11+, oder ähnlich

### Empfohlen (Produktion)
- **CPU:** 4 Kerne
- **RAM:** 8 GB
- **Storage:** 100 GB SSD (RAID 1 empfohlen)
- **OS:** Ubuntu 22.04 LTS
- **Netzwerk:** 1 Gbit/s

### Software-Anforderungen
- Python 3.11+
- PostgreSQL 15+
- Node.js 18+
- Docker & Docker Compose (optional)
- Nginx (für Produktion)

---

## Schnellstart (Entwicklung)

### 1. Repository klonen

```bash
git clone <repository-url>
cd ai
```

### 2. Setup-Skript ausführen

```bash
chmod +x setup.sh
./setup.sh
```

Das Skript:
- Erstellt `.env` aus `.env.example`
- Installiert Python- und Node-Dependencies
- Erstellt Datenbank-Tabellen
- Erstellt Admin-Benutzer

### 3. Encryption Keys generieren

```bash
# Generiere Keys
python3 -c "from cryptography.fernet import Fernet; print('MASTER_ENCRYPTION_KEY=' + Fernet.generate_key().decode())"
python3 -c "from cryptography.fernet import Fernet; print('FIELD_ENCRYPTION_KEY=' + Fernet.generate_key().decode())"

# Füge Keys in .env ein!
```

### 4. Backend starten

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

Backend läuft auf: `http://localhost:8000`
API Docs: `http://localhost:8000/api/v1/docs`

### 5. Frontend starten

```bash
cd frontend
npm run dev
```

Frontend läuft auf: `http://localhost:3000`

### 6. Login

- **Username:** admin
- **Password:** admin123
- **⚠️ WICHTIG:** Passwort sofort ändern!

---

## Produktions-Deployment

### Variante A: Cloud-Hosting (Hetzner)

#### 1. Server erstellen

```bash
# Hetzner Cloud CLI
hcloud server create \
  --name patientenakte-prod \
  --type cx31 \
  --image ubuntu-22.04 \
  --location nbg1 \
  --ssh-key <your-key>
```

#### 2. Server konfigurieren

```bash
# SSH zum Server
ssh root@<server-ip>

# System aktualisieren
apt update && apt upgrade -y

# Dependencies installieren
apt install -y python3.11 python3.11-venv postgresql-15 nginx certbot python3-certbot-nginx
```

#### 3. PostgreSQL einrichten

```bash
# PostgreSQL-User erstellen
sudo -u postgres createuser -P patientenakte

# Datenbank erstellen
sudo -u postgres createdb -O patientenakte patientenakte_db

# Erlaube lokale Verbindungen
sudo nano /etc/postgresql/15/main/pg_hba.conf
# Füge hinzu:
# local   patientenakte_db   patientenakte   md5
```

#### 4. Anwendung deployen

```bash
# User erstellen
useradd -m -s /bin/bash patientenakte
su - patientenakte

# Code auschecken
git clone <repository-url> /opt/patientenakte
cd /opt/patientenakte

# Setup ausführen
./setup.sh

# Systemd-Service erstellen
sudo nano /etc/systemd/system/patientenakte.service
```

**patientenakte.service:**

```ini
[Unit]
Description=DSGVO-Patientenaktensystem
After=network.target postgresql.service

[Service]
Type=notify
User=patientenakte
Group=patientenakte
WorkingDirectory=/opt/patientenakte/backend
Environment="PATH=/opt/patientenakte/backend/venv/bin"
ExecStart=/opt/patientenakte/backend/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

#### 5. Nginx konfigurieren

```bash
sudo nano /etc/nginx/sites-available/patientenakte
```

**Nginx-Konfiguration:**

```nginx
server {
    listen 80;
    server_name patientenakte.example.com;

    # SSL-Redirect
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name patientenakte.example.com;

    # SSL-Zertifikate (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/patientenakte.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/patientenakte.example.com/privkey.pem;

    # SSL-Konfiguration
    ssl_protocols TLSv1.3 TLSv1.2;
    ssl_ciphers 'ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers on;

    # HSTS
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Security Headers
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Backend API
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Frontend
    location / {
        root /opt/patientenakte/frontend/dist;
        try_files $uri $uri/ /index.html;
    }
}
```

#### 6. SSL-Zertifikat einrichten

```bash
sudo certbot --nginx -d patientenakte.example.com
```

#### 7. Services starten

```bash
# Backend
sudo systemctl enable patientenakte
sudo systemctl start patientenakte

# Nginx
sudo systemctl enable nginx
sudo systemctl restart nginx
```

---

## Docker-Deployment

### Produktions-Docker-Compose

**docker-compose.prod.yml:**

```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    restart: always
    environment:
      POSTGRES_DB: patientenakte_db
      POSTGRES_USER: patientenakte
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - /opt/data/postgres:/var/lib/postgresql/data
    networks:
      - internal

  backend:
    build: ./backend
    restart: always
    depends_on:
      - db
    environment:
      - DATABASE_URL=postgresql://patientenakte:${DB_PASSWORD}@db:5432/patientenakte_db
      - MASTER_ENCRYPTION_KEY=${MASTER_ENCRYPTION_KEY}
      - FIELD_ENCRYPTION_KEY=${FIELD_ENCRYPTION_KEY}
      - SECRET_KEY=${SECRET_KEY}
    volumes:
      - /opt/data/backups:/opt/backups
      - /opt/data/logs:/var/log/patientenakte
    networks:
      - internal

  frontend:
    build: ./frontend
    restart: always
    depends_on:
      - backend
    networks:
      - internal

  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - /etc/letsencrypt:/etc/letsencrypt:ro
    depends_on:
      - backend
      - frontend
    networks:
      - internal

networks:
  internal:
    driver: bridge
```

### Deployment

```bash
# Bauen und starten
docker-compose -f docker-compose.prod.yml up -d

# Logs anzeigen
docker-compose -f docker-compose.prod.yml logs -f

# Datenbank-Migrationen
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

---

## Sicherheits-Checkliste

### Vor Produktivbetrieb PRÜFEN:

- [ ] **Verschlüsselungs-Keys generiert** (MASTER_ENCRYPTION_KEY, FIELD_ENCRYPTION_KEY)
- [ ] **SECRET_KEY geändert** (mindestens 32 Zeichen)
- [ ] **Admin-Passwort geändert**
- [ ] **MFA für alle Admins aktiviert**
- [ ] **SSL/TLS-Zertifikat installiert** (Let's Encrypt)
- [ ] **Firewall konfiguriert** (nur 80, 443 offen)
- [ ] **PostgreSQL Passwort stark** (min. 20 Zeichen)
- [ ] **Automatische Backups eingerichtet**
- [ ] **DSFA ausgefüllt und genehmigt**
- [ ] **AVV mit Hosting-Anbieter abgeschlossen**
- [ ] **Datenschutzerklärung auf Website**
- [ ] **Audit-Logging aktiviert**
- [ ] **Fail2Ban installiert** (Brute-Force-Schutz)

---

## Backup & Recovery

### Automatisches Backup-Skript

**backup.sh:**

```bash
#!/bin/bash

BACKUP_DIR="/opt/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="patientenakte_db"
DB_USER="patientenakte"

# PostgreSQL Dump
pg_dump -U $DB_USER $DB_NAME | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Verschlüssele Backup
gpg --encrypt --recipient admin@example.com $BACKUP_DIR/db_$DATE.sql.gz

# Lösche alte Backups (älter als 365 Tage)
find $BACKUP_DIR -name "db_*.sql.gz.gpg" -mtime +365 -delete

echo "Backup erstellt: db_$DATE.sql.gz.gpg"
```

### Cronjob einrichten

```bash
# Täglich um 2 Uhr nachts
0 2 * * * /opt/patientenakte/backup.sh
```

### Recovery

```bash
# Backup entschlüsseln
gpg --decrypt db_20250108_020000.sql.gz.gpg > db_restore.sql.gz

# Datenbank wiederherstellen
gunzip db_restore.sql.gz
psql -U patientenakte patientenakte_db < db_restore.sql
```

---

## Monitoring

### Health-Check-Skript

```bash
#!/bin/bash

# Prüfe Backend
if ! curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "Backend ist down!" | mail -s "Patientenakte Alert" admin@example.com
    systemctl restart patientenakte
fi

# Prüfe Festplatte
USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $USAGE -gt 80 ]; then
    echo "Festplatte zu $USAGE% voll!" | mail -s "Speicher-Warnung" admin@example.com
fi
```

### Prometheus-Integration (optional)

```python
# In app/main.py hinzufügen:
from prometheus_client import Counter, Histogram, make_asgi_app

REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP Requests')
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP Request Latency')

# Mount Metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)
```

---

## Troubleshooting

### Backend startet nicht

```bash
# Logs prüfen
journalctl -u patientenakte -f

# Datenbank-Verbindung testen
psql -U patientenakte -h localhost patientenakte_db
```

### Hohe CPU-Last

```bash
# Slow Queries finden
sudo -u postgres psql patientenakte_db
SELECT * FROM pg_stat_activity WHERE state = 'active';
```

### Audit-Logs zu groß

```bash
# Alte Logs archivieren
find /var/log/patientenakte -name "audit.log.*" -mtime +730 -exec gzip {} \;
```

---

**Bei Fragen:**
- Dokumentation: `docs/`
- Support: support@example.com
