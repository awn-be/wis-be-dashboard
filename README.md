# WIS-BE Dashboard

Saubere Trennung von **interner Issue-Pflege** und **öffentlicher Anzeige**:

```text
GitHub Issues + GitHub Projects
             │
             │ GitHub Action (1x pro Tag um 05:10 Uhr)
             ▼
       dashboard.json
             │
             ▼
        GitHub Pages
             │
             ▼
      ArcGIS Portal iFrame (WIS-BE Homepage)
```

Dadurch ruft der Browser der Portal-Besucher **nicht mehr direkt die GitHub API** auf.

## Konfigurierte Zuordnung

| Repository | Anzeige | GitHub Project |
|---|---|---:|
| `awn-be/vertigis_admin` | Allgemeine Verbesserungen | #6 – Sprintplanung Admin |
| `awn-be/vertigis_waldschutz` | Waldschadenmeldung | #7 – Sprintplanung Waldschutz |

## Übersetzungen

**Status**

- `Todo` → Geplant
- `In progress` → In Arbeit
- `Ready to test` → Bereit zum Testen
- `Done` → Erledigt

**Priority**

- `Urgent` → Sehr hoch
- `High` → Hoch
- `Medium` → Mittel
- `Low` → Niedrig

**Type**

- `Bug` → Fehler
- `Feature` → Funktion
- `Task` → Aufgabe

## 1. Neues öffentliches Repository anlegen

Zum Beispiel:

`awn-be/wis-be-dashboard`

Danach den **gesamten Inhalt dieses ZIPs** in das Repository laden. Wichtig: Der Ordner `.github/workflows` muss ebenfalls vorhanden sein.

## 2. Token für die Sprintplanungs-Projects hinterlegen

Die Action benötigt Zugriff auf die GitHub Projects der Organisation.

Empfohlen ist ein **Fine-grained Personal Access Token** mit Leserechten für die benötigten Ressourcen, insbesondere:

- Organization permission: **Projects – Read-only**
- Repository access auf `vertigis_admin` und `vertigis_waldschutz` (für Issues/Metadaten, soweit durch eure Org-Einstellungen erforderlich)

Danach im Dashboard-Repository:

**Settings → Secrets and variables → Actions → New repository secret**

Name:

`DASHBOARD_TOKEN`

Wert:

den erzeugten Token einfügen.

> Der Token landet nie in `index.html` oder `dashboard.json`. Er steht nur der GitHub Action als Secret zur Verfügung.

## 3. Action einmal manuell starten

Im Repository:

**Actions → Dashboard aktualisieren → Run workflow**

Wenn alles passt, wird danach `dashboard.json` automatisch mit euren echten Issues, Prioritäten und Project-Statuswerten gefüllt.

Anschliessend läuft die Action automatisch einmal pro Tag um 05:00 Uhr.

## 4. GitHub Pages aktivieren

Im Repository:

**Settings → Pages**

Unter **Build and deployment**:

- Source: `Deploy from a branch`
- Branch: `main`
- Folder: `/ (root)`

Speichern.

Danach erhältst du eine URL in dieser Art:

`https://awn-be.github.io/wis-be-dashboard/`

Diese URL kannst du anschliessend als iframe in ArcGIS Portal verwenden.

## Lokal testen

`index.html` verwendet jetzt nur noch `dashboard.json` aus demselben Ordner. Für einen realistischen lokalen Test am besten einen kleinen Webserver verwenden:

```bash
python -m http.server 8000
```

Dann:

`http://localhost:8000`

Ein direktes Doppelklicken auf `index.html` kann je nach Browser bei lokalen `file://`-Zugriffen auf `dashboard.json` blockiert werden. Das ist kein Problem auf GitHub Pages.

## Neue Repository-Sektion ergänzen

Nur `config.json` erweitern, z. B.:

```json
{
  "repo": "vertigis_planungsgrundlagen",
  "title": "Planungsgrundlagen",
  "project_number": 8,
  "project_title": "Sprintplanung Planungsgrundlagen"
}
```

Beim nächsten Lauf der Action wird die neue Sektion automatisch in `dashboard.json` aufgenommen.

## Dateien

- `index.html` – öffentliche, responsive Anzeige
- `dashboard.json` – automatisch erzeugte Daten
- `config.json` – Repository-/Project-Zuordnung und Übersetzungen
- `scripts/update_dashboard.py` – liest GitHub aus und erzeugt JSON
- `.github/workflows/update-dashboard.yml` – automatische Aktualisierung
