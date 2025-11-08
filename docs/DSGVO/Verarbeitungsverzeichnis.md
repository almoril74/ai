# Verzeichnis von Verarbeitungstätigkeiten
## Gem. Art. 30 DSGVO

**Verantwortlicher:** [Name der Osteopathiepraxis]
**Adresse:** [Praxisadresse]
**Kontakt:** [E-Mail/Telefon]
**Datenschutzbeauftragter:** [Name, Kontakt]
**Stand:** 2025-01-08

---

## Verarbeitungstätigkeit 1: Digitale Patientenakte

### 1. Name und Kontaktdaten des Verantwortlichen

**Verantwortlicher:**
[Name der Praxis / Praxisinhaber]
[Adresse]
[E-Mail]
[Telefon]

**Gemeinsam Verantwortlicher:** Nicht zutreffend

**Datenschutzbeauftragter:**
[Name]
[E-Mail]

---

### 2. Zwecke der Verarbeitung

- **Primärer Zweck:** Verwaltung und Dokumentation von Patientendaten zur Gewährleistung ordnungsgemäßer osteopathischer Behandlung
- **Sekundäre Zwecke:**
  - Erfüllung der Dokumentationspflicht gem. § 630f BGB
  - Terminverwaltung
  - Abrechnung von Leistungen
  - Qualitätssicherung

---

### 3. Kategorien betroffener Personen

- Patienten (aktuelle und ehemalige)
- Interessenten (Anfragen)
- Gesetzliche Vertreter von Patienten

---

### 4. Kategorien personenbezogener Daten

#### 4.1 Stammdaten
- Vor- und Nachname
- Geburtsdatum
- Geschlecht
- Adresse
- Telefonnummer
- E-Mail-Adresse

#### 4.2 Gesundheitsdaten (Art. 9 DSGVO)
- Anamnese (Krankengeschichte)
- Aktuelle Beschwerden
- Diagnosen
- Behandlungsdokumentation
- Befunde und Untersuchungsergebnisse
- Therapieverlauf
- Allergien
- Medikation
- Vorerkrankungen

#### 4.3 Abrechnungsdaten
- Rechnungsdaten
- Zahlungsinformationen (keine Kreditkartendaten)

#### 4.4 Technische Daten
- Login-Daten (für Patienten-Portal, falls vorhanden)
- IP-Adressen (Audit-Logging)
- Zugriffsprotokolle

---

### 5. Kategorien von Empfängern

#### Interne Empfänger:
- Behandelnde Osteopathen
- Autorisiertes Praxispersonal (nach RBAC)

#### Externe Empfänger:
- **IT-Dienstleister** (Hosting, Wartung) - mit AVV
- **Abrechnungsdienstleister** (falls vorhanden) - mit AVV
- **Gesetzliche Krankenversicherungen** (nur mit Patienteneinwilligung)
- **Private Krankenversicherungen** (nur mit Patienteneinwilligung)
- **Andere Behandler** (nur mit Patienteneinwilligung)

#### Keine Übermittlung an:
- Drittländer außerhalb EU/EWR

---

### 6. Übermittlung an Drittländer

**Keine** Übermittlung an Drittländer oder internationale Organisationen geplant.

Falls in Zukunft erforderlich:
- Nur mit geeigneten Garantien (Art. 46 DSGVO)
- Z.B. EU-Standardvertragsklauseln

---

### 7. Fristen für die Löschung

| Datenkategorie | Aufbewahrungsfrist | Rechtsgrundlage |
|----------------|-------------------|-----------------|
| **Behandlungsdokumentation** | 10 Jahre ab letzter Behandlung | § 630f BGB |
| **Abrechnungsdaten** | 10 Jahre | § 147 AO |
| **Einwilligungserklärungen** | Bis Widerruf + 3 Jahre | Art. 7 DSGVO |
| **Audit-Logs** | 2 Jahre | IT-Sicherheit |
| **Anfragen (ohne Behandlung)** | 6 Monate | Berechtigtes Interesse |

**Automatische Löschung:** System markiert Daten automatisch zur Löschung nach Ablauf der Frist.

---

### 8. Technische und organisatorische Maßnahmen (TOM)

#### 8.1 Zutrittskontrolle
- ✅ Gesicherter Serverraum (bei On-Premise)
- ✅ Zutritt nur für autorisiertes Personal
- ✅ Besucherbuch / Zugangsprotokolle

#### 8.2 Zugangskontrolle
- ✅ Individuelle Benutzerkonten (keine Shared Accounts)
- ✅ Sichere Passwörter (min. 12 Zeichen, Komplexität)
- ✅ Multi-Faktor-Authentifizierung (MFA)
- ✅ Automatische Session-Timeouts (60 Min.)
- ✅ Account-Sperrung nach Fehlversuchen

#### 8.3 Zugriffskontrolle
- ✅ Rollenbasierte Zugriffskontrolle (RBAC)
  - Admin: Volle Rechte
  - Doctor: Patienten-CRUD, Behandlungen
  - Assistant: Eingeschränkter Zugriff
  - ReadOnly: Nur Lesezugriff
- ✅ Audit-Logging aller Zugriffe
- ✅ Need-to-know-Prinzip

#### 8.4 Weitergabekontrolle
- ✅ Verschlüsselte Übertragung (TLS 1.3)
- ✅ End-to-End-Verschlüsselung bei E-Mail (optional)
- ✅ Protokollierung aller Datenexporte

#### 8.5 Eingabekontrolle
- ✅ Audit-Logging aller Änderungen
- ✅ Versionierung von Änderungen
- ✅ Nachvollziehbarkeit: Wer, Was, Wann

#### 8.6 Auftragskontrolle
- ✅ AVV mit allen Dienstleistern
- ✅ Regelmäßige Kontrolle der Dienstleister
- ✅ Weisungsbefugnis dokumentiert

#### 8.7 Verfügbarkeitskontrolle
- ✅ Tägliche verschlüsselte Backups
- ✅ 3-2-1-Backup-Strategie
- ✅ Regelmäßige Restore-Tests
- ✅ Unterbrechungsfreie Stromversorgung (USV)
- ✅ Redundante Systeme (bei kritischen Komponenten)

#### 8.8 Trennungskontrolle
- ✅ Logische Trennung verschiedener Mandanten (falls Multi-Tenant)
- ✅ Separate Umgebungen: Entwicklung, Test, Produktion
- ✅ Verschlüsselung verhindert Datenvermischung

#### 8.9 Verschlüsselung
- ✅ **Transport:** TLS 1.3
- ✅ **At-Rest:** AES-256 Feld-Level-Verschlüsselung
- ✅ **Backups:** Verschlüsselt
- ✅ **Pseudonymisierung:** SHA-256-Hash für Patienten-IDs

#### 8.10 Incident Response
- ✅ Datenschutzverletzungs-Verfahren etabliert
- ✅ Meldung an Aufsichtsbehörde innerhalb 72h
- ✅ Benachrichtigung betroffener Personen
- ✅ Incident-Response-Team definiert

#### 8.11 Datenschutzmanagement
- ✅ Datenschutz-Folgenabschätzung (DSFA) durchgeführt
- ✅ Privacy by Design / Privacy by Default
- ✅ Regelmäßige Schulungen
- ✅ Datenschutzrichtlinien dokumentiert

---

### 9. Rechtsgrundlage der Verarbeitung

#### Primäre Rechtsgrundlagen:
- **Art. 9 Abs. 2 lit. a DSGVO:** Explizite Einwilligung für Gesundheitsdaten
- **Art. 6 Abs. 1 lit. b DSGVO:** Vertragserfüllung (Behandlungsvertrag)
- **Art. 6 Abs. 1 lit. c DSGVO:** Rechtliche Verpflichtung (§ 630f BGB)
- **Art. 6 Abs. 1 lit. f DSGVO:** Berechtigtes Interesse (Praxisverwaltung)

#### Besondere Kategorien:
- **Art. 9 Abs. 3 DSGVO i.V.m. § 22 BDSG:** Verarbeitung von Gesundheitsdaten für Gesundheitsvorsorge

---

### 10. Betroffenenrechte

Die Praxis gewährleistet folgende Rechte:

| Recht | Umsetzung |
|-------|-----------|
| **Auskunftsrecht (Art. 15)** | Auf Anfrage: Kopie aller Daten innerhalb 1 Monat |
| **Berichtigung (Art. 16)** | Korrektur unrichtiger Daten |
| **Löschung (Art. 17)** | Löschung nach Widerruf (sofern keine Aufbewahrungspflicht) |
| **Einschränkung (Art. 18)** | Sperrung anstelle Löschung |
| **Datenübertragbarkeit (Art. 20)** | Export in CSV/JSON-Format |
| **Widerspruch (Art. 21)** | Widerspruch gegen Verarbeitung möglich |
| **Widerruf Einwilligung (Art. 7 Abs. 3)** | Jederzeit widerrufbar |

**Kontakt für Ausübung der Rechte:**
[E-Mail/Telefon der Praxis]

---

### 11. Auftragsverarbeiter (AVV)

| Dienstleister | Leistung | AVV vorhanden | Standort |
|---------------|----------|---------------|----------|
| [Hosting-Anbieter] | Server-Hosting | ✅ Ja | Deutschland |
| [Backup-Anbieter] | Backup-Storage | ✅ Ja | Deutschland |
| [Wartung] | System-Wartung | ✅ Ja | Deutschland |

**Keine Subauftragsverarbeiter ohne vorherige schriftliche Genehmigung.**

---

### 12. Datenschutzbeauftragte/r

**Pflicht zur Benennung:**
- ☐ Ja (falls >20 Personen regelmäßig mit personenbezogenen Daten arbeiten)
- ☑ Nein (kleiner Betrieb, aber freiwillige Benennung empfohlen)

**Kontakt:**
[Name]
[E-Mail]
[Telefon]

---

### 13. Sonstige Hinweise

- Dieses Verzeichnis wird jährlich überprüft und aktualisiert
- Bei wesentlichen Änderungen erfolgt eine unverzügliche Anpassung
- Dokumentation wird mind. 3 Jahre aufbewahrt

**Letzte Aktualisierung:** 2025-01-08
**Nächste Überprüfung:** 2026-01-08
**Verantwortlich:** [Name]

---

**Unterschrift Verantwortlicher:**
_______________________________

**Datum:**
_______________________________
