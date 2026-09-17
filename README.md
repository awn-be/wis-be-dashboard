# WIS-BE Dashboard

Saubere Trennung von **interner Issue-Pflege** (GitHub) und
**öffentlicher Anzeige** (WIS-BE Homepage):

``` text
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
       ArcGIS Portal iFrame
```

Die GitHub-Daten werden automatisch in `dashboard.json` aufbereitet und von der öffentlichen Seite ausschliesslich aus dieser Datei geladen.
Dadurch greift die öffentliche Anzeige **nicht direkt auf die GitHub API** zu.

## Dateien

-   `index.html` -- öffentliche, responsive Anzeige
-   `dashboard.json` -- automatisch erzeugte Dashboard-Daten
-   `config.json` -- Repository-/Project-Zuordnung und Übersetzungen
-   `scripts/update_dashboard.py` -- liest GitHub aus und erzeugt
    `dashboard.json`
-   `.github/workflows/update-dashboard.yml` -- automatische tägliche
    Aktualisierung

## Konfigurierte Zuordnung

| Repository | Anzeige | GitHub Project |
| --- | --- | --- |
| `awn-be/vertigis_admin` | Allgemeine Verbesserungen | #6 – Sprintplanung Admin |
| `awn-be/vertigis_waldschutz` | Waldschadenmeldung | #7 – Sprintplanung Waldschutz |

## Übersetzungen

**Status**

-   `Todo` → Geplant
-   `In progress` → In Arbeit
-   `Ready to test` → Bereit zum Testen
-   `Done` → Erledigt

**Priority**

-   `Urgent` → Sehr hoch
-   `High` → Hoch
-   `Medium` → Mittel
-   `Low` → Niedrig

**Type**

-   `Bug` → Fehler
-   `Feature` → Funktion
-   `Task` → Aufgabe

## Neue Repository-Sektion ergänzen

Für eine zusätzliche Dashboard-Sektion muss lediglich `config.json` um
das entsprechende Repository und GitHub Project erweitert werden, z. B.:

``` json
{
  "repo": "vertigis_planungsgrundlagen",
  "title": "Planungsgrundlagen",
  "project_number": 8,
  "project_title": "Sprintplanung Planungsgrundlagen"
}
```

Beim nächsten Lauf der Action wird die neue Sektion automatisch in
`dashboard.json` aufgenommen.

------------------------------------------------------------------------

# Dokumentation der Einrichtung

Die folgenden Abschnitte dokumentieren die ursprüngliche Einrichtung des
WIS-BE Dashboards. Sie dienen als technische Retrospektive und sind für
den laufenden Betrieb nicht erforderlich.

## 1. Öffentliches Repository

Für das Dashboard wurde das öffentliche Repository
`awn-be/wis-be-dashboard` angelegt. Darin wurden die Dateien für die
öffentliche Anzeige, die Konfiguration sowie die automatische
Aktualisierung abgelegt.

Der GitHub-Workflow befindet sich unter
`.github/workflows/update-dashboard.yml`.

## 2. Zugriff auf GitHub Projects

Damit die GitHub Action neben den öffentlichen Issues auch die
Statuswerte aus den GitHub Projects auslesen kann, wurde ein
**Fine-grained Personal Access Token** eingerichtet.

Der Token erhielt Leserechte auf die benötigten Ressourcen,
insbesondere:

-   Organization permission: **Projects -- Read-only**
-   Repository access auf `vertigis_admin` und `vertigis_waldschutz`
    (für Issues/Metadaten, soweit durch die Org-Einstellungen
    erforderlich)

Im Dashboard-Repository wurde der Token anschliessend als Actions Secret
hinterlegt:

**Settings → Secrets and variables → Actions**

Name: `DASHBOARD_TOKEN`

> Der Token ist weder Bestandteil von `index.html` noch von
> `dashboard.json`. Er steht ausschliesslich der GitHub Action als
> Secret zur Verfügung.

## 3. GitHub Action

Für die Erzeugung von `dashboard.json` wurde der Workflow **Dashboard
aktualisieren** eingerichtet.

Bei der Einrichtung wurde der Workflow zunächst manuell über **Actions →
Dashboard aktualisieren → Run workflow** ausgeführt. Dadurch konnte
geprüft werden, ob Issues, Prioritäten und Project-Statuswerte korrekt
in `dashboard.json` übernommen werden.

Anschliessend wurde die automatische Aktualisierung auf **einmal pro Tag
um 05:10 Uhr (`Europe/Zurich`)** eingestellt. Die Ausführung erfolgt
bewusst nicht exakt zur vollen Stunde.

> **Hinweis zur automatischen Aktualisierung:**  
> Geplante GitHub-Actions-Workflows werden nicht zwingend exakt zum
> konfigurierten Zeitpunkt ausgeführt. Der tatsächliche Start kann sich
> verzögern. Bei der Einrichtung und beim Test des Dashboards wurden
> teilweise deutliche Verzögerungen beobachtet. Für die tägliche
> Aktualisierung des Dashboards ist dies unkritisch.

Die Action führt `scripts/update_dashboard.py` aus und schreibt
Änderungen an `dashboard.json` zurück in das Repository.

## 4. GitHub Pages

Nach erfolgreicher Datenübernahme wurde GitHub Pages für das Dashboard
aktiviert.

Unter **Settings → Pages → Build and deployment** wurden folgende
Einstellungen verwendet:

-   Source: `Deploy from a branch`
-   Branch: `main`
-   Folder: `/ (root)`

Das Dashboard ist dadurch unter folgender Adresse erreichbar:

`https://awn-be.github.io/wis-be-dashboard/`

Diese GitHub-Pages-Seite kann anschliessend per iFrame in ArcGIS Portal
eingebunden werden.

## KI-Unterstützung

Dieses Repository und das WIS-BE Dashboard wurden mit Unterstützung von
**ChatGPT (OpenAI; bei der aktuellen Umsetzung: GPT-5.6 Sol)** konzipiert
und umgesetzt.

Die KI-Unterstützung wurde insbesondere bei der Konzeption der Architektur,
der Entwicklung und Überarbeitung von Python-, HTML-, CSS- und
JavaScript-Code sowie bei der technischen Dokumentation eingesetzt.

Die fachlichen Anforderungen, Entscheidungen, Tests und die Freigabe der
Umsetzung erfolgten durch die Projektverantwortlichen.
