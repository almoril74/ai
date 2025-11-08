# Datenschutz-Folgenabschätzung (DSFA)
## Digitales Patientenaktensystem für Osteopathiepraxis

**Erstellt am:** 2025-01-08
**Version:** 1.0
**Verantwortlich:** [Name des Datenschutzbeauftragten]

---

## 1. Beschreibung der geplanten Verarbeitungsvorgänge

### 1.1 Zweck der Verarbeitung
Digitale Verwaltung von Patientenakten in einer Osteopathiepraxis zur Erfüllung der Dokumentationspflicht gem. § 630f BGB sowie zur effizienten Patientenversorgung.

### 1.2 Art der verarbeiteten Daten

**Personenbezogene Daten:**
- Vorname, Nachname
- Geburtsdatum
- Adresse, Telefon, E-Mail

**Gesundheitsdaten (Art. 9 DSGVO):**
- Anamnese (Krankengeschichte)
- Diagnosen
- Behandlungsdokumentation
- Befunde
- Allergien
- Medikation
- Vorerkrankungen

**Technische Daten:**
- IP-Adressen (für Audit-Logging)
- Login-Zeitpunkte
- Zugriffsprotokolle

### 1.3 Betroffene Personen
- Patienten der Osteopathiepraxis
- Mitarbeiter (für Authentifizierung und Zugriffskontrolle)

### 1.4 Empfänger der Daten
- Behandelnde Osteopathen
- Berechtigtes Praxispersonal
- Keine Weitergabe an Dritte (außer mit expliziter Einwilligung oder gesetzlicher Pflicht)

---

## 2. Bewertung der Notwendigkeit und Verhältnismäßigkeit

### 2.1 Rechtsgrundlage
- **Art. 9 Abs. 2 lit. a DSGVO:** Explizite Einwilligung für Gesundheitsdaten
- **Art. 6 Abs. 1 lit. f DSGVO:** Berechtigtes Interesse (Dokumentationspflicht)
- **§ 630f BGB:** Dokumentationspflicht für Behandlungen
- **§ 203 StGB:** Berufsgeheimnis

### 2.2 Notwendigkeit
Die Verarbeitung ist notwendig zur:
- Erfüllung gesetzlicher Dokumentationspflichten
- Gewährleistung qualitativ hochwertiger Patientenversorgung
- Nachvollziehbarkeit von Behandlungsverläufen

### 2.3 Verhältnismäßigkeit
- Datenminimierung: Nur erforderliche Daten werden erhoben
- Zweckbindung: Daten werden nur für Behandlungszwecke verwendet
- Speicherbegrenzung: 10 Jahre gem. § 630f BGB, danach Löschung

---

## 3. Risikobewertung für Rechte und Freiheiten der Betroffenen

### 3.1 Identifizierte Risiken

| Risiko | Schweregrad | Eintrittswahrscheinlichkeit | Gesamtrisiko |
|--------|-------------|----------------------------|--------------|
| Unbefugter Zugriff auf Gesundheitsdaten | **Hoch** | Mittel | **Hoch** |
| Datenverlust durch technisches Versagen | Mittel | Niedrig | Mittel |
| Identitätsdiebstahl | Hoch | Niedrig | Mittel |
| Datenmanipulation | Mittel | Niedrig | Niedrig-Mittel |
| Verstoß gegen Berufsgeheimnis (§ 203 StGB) | **Hoch** | Niedrig | Mittel-Hoch |

### 3.2 Mögliche Folgen für Betroffene
- **Unbefugter Zugriff:** Verletzung der Vertraulichkeit sensibler Gesundheitsdaten
- **Datenverlust:** Unterbrechung der Behandlungskontinuität
- **Identitätsdiebstahl:** Missbrauch personenbezogener Daten
- **Rufschädigung:** Bei Offenlegung sensibler Diagnosen

---

## 4. Maßnahmen zur Bewältigung der Risiken

### 4.1 Technische Maßnahmen

#### Verschlüsselung
- ✅ **AES-256 Feld-Level-Verschlüsselung** für alle sensitiven Daten
- ✅ **TLS 1.3** für Datenübertragung
- ✅ **Verschlüsselte Backups**
- ✅ **Pseudonymisierung** von Patienten-IDs

**Risikominderung:** Hoch → Niedrig

#### Zugriffskontrolle
- ✅ **Multi-Faktor-Authentifizierung (MFA)** für alle Benutzer
- ✅ **Rollenbasierte Zugriffskontrolle (RBAC)**
- ✅ **Session-Timeout** nach 60 Minuten Inaktivität
- ✅ **IP-Whitelisting** für Admin-Zugriff
- ✅ **Account-Sperrung** nach 5 fehlgeschlagenen Login-Versuchen

**Risikominderung:** Hoch → Niedrig-Mittel

#### Audit-Logging
- ✅ **Vollständige Protokollierung** aller Datenzugriffe
- ✅ **Unveränderbare Logs** (Write-Only)
- ✅ **Retention:** 2 Jahre
- ✅ **Automatische Anomalie-Erkennung** (optional)

**Risikominderung:** Mittel → Niedrig

#### Backup & Recovery
- ✅ **Tägliche verschlüsselte Backups**
- ✅ **3-2-1-Regel:** 3 Kopien, 2 Medien, 1 Offsite
- ✅ **Regelmäßige Restore-Tests**
- ✅ **Retention:** 365 Tage

**Risikominderung:** Mittel → Niedrig

### 4.2 Organisatorische Maßnahmen

#### Schulung
- ✅ Jährliche Datenschutzschulung für alle Mitarbeiter
- ✅ Sensibilisierung für Phishing und Social Engineering
- ✅ Dokumentation der Schulungen

#### Richtlinien
- ✅ Datenschutzrichtlinie
- ✅ Passwort-Richtlinie (min. 12 Zeichen, Komplexität)
- ✅ Clear-Desk-Policy
- ✅ Incident-Response-Plan

#### Verträge
- ✅ **AVV** mit Hosting-Anbieter (falls Cloud)
- ✅ **NDA** für alle Mitarbeiter
- ✅ Verpflichtung auf Berufsgeheimnis (§ 203 StGB)

### 4.3 Betroffenenrechte

| Recht | Umsetzung |
|-------|-----------|
| **Auskunftsrecht (Art. 15)** | API-Endpoint für Patienten-Datenexport |
| **Berichtigungsrecht (Art. 16)** | Update-Funktionen in UI |
| **Löschrecht (Art. 17)** | Soft-Delete mit Retention-Logik |
| **Einschränkung (Art. 18)** | Deaktivierung von Patienten-Accounts |
| **Datenübertragbarkeit (Art. 20)** | CSV/JSON-Export |
| **Widerspruchsrecht (Art. 21)** | Einwilligungsverwaltung |

---

## 5. Konsultation und Freigabe

### 5.1 Interne Konsultation
- ☐ Datenschutzbeauftragter konsultiert
- ☐ IT-Sicherheitsbeauftragter konsultiert
- ☐ Geschäftsleitung informiert

### 5.2 Externe Konsultation (falls erforderlich)
- ☐ Aufsichtsbehörde konsultiert (bei hohem Restrisiko)

### 5.3 Freigabe
- ☐ DSFA genehmigt durch: ___________________________
- ☐ Datum: ___________________________

---

## 6. Bewertung des Restrisikos

Nach Implementierung aller Schutzmaßnahmen:

| Risiko | Ursprünglich | Nach Maßnahmen | Akzeptabel? |
|--------|--------------|----------------|-------------|
| Unbefugter Zugriff | Hoch | **Niedrig-Mittel** | ✅ Ja |
| Datenverlust | Mittel | **Niedrig** | ✅ Ja |
| Identitätsdiebstahl | Mittel | **Niedrig** | ✅ Ja |
| Datenmanipulation | Niedrig-Mittel | **Niedrig** | ✅ Ja |

**Gesamtbewertung:** Das Restrisiko ist nach Umsetzung aller Maßnahmen **akzeptabel**.

---

## 7. Überwachung und Überprüfung

- ✅ **Jährliche Überprüfung** dieser DSFA
- ✅ **Ad-hoc-Überprüfung** bei wesentlichen Änderungen am System
- ✅ **Regelmäßige Sicherheits-Audits**
- ✅ **Penetrationstests** (alle 2 Jahre)

**Nächste Überprüfung:** 2026-01-08

---

## 8. Dokumentation der Entscheidung

Diese DSFA kommt zu dem Ergebnis, dass die geplante Verarbeitung von Gesundheitsdaten im digitalen Patientenaktensystem **rechtmäßig und verhältnismäßig** ist, sofern alle beschriebenen technischen und organisatorischen Maßnahmen implementiert werden.

Das verbleibende Restrisiko ist **vertretbar** und steht in angemessenem Verhältnis zum verfolgten Zweck (Patientenversorgung und Erfüllung gesetzlicher Pflichten).

---

**Unterschrift Verantwortlicher:**
_______________________________

**Unterschrift Datenschutzbeauftragter:**
_______________________________

**Datum:**
_______________________________
