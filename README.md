# WIS-BE Dashboard

Saubere Trennung von **interner Issue-Pflege** (GitHub) und
**öffentlicher Anzeige** (WIS-BE Homepage):

``` text
GitHub Issues + GitHub Projects
             │
             │ GitHub Action (automatisch, nachts)
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
| `awn-be/vertigis_fschutz_wschad` | Waldschaden erfassen, abrechnen und melden | #7 – Sprintplanung Waldschaden |

Das Repository bestimmt, in welcher Sektion ein Issue im Dashboard
angezeigt wird. Für den Status wird ausschliesslich das für diese
Sektion konfigurierte GitHub Project berücksichtigt.

Ist ein Issue zusätzlich weiteren GitHub Projects zugeordnet, haben
deren Statuswerte keinen Einfluss auf die Anzeige im Dashboard.

## Sichtbarkeit von Issues

Über das organisationsweite GitHub Issue Field `Visibility` wird gesteuert,
welche Issues in das öffentliche WIS-BE Dashboard übernommen werden.

Das Feld ist als Single-Select-Feld mit folgenden Werten definiert:

-   `Public` → wird im öffentlichen Dashboard angezeigt
-   `Internal` → wird nicht ins öffentliche Dashboard übernommen

Issues mit `Visibility = Internal` werden bereits beim Erzeugen von
`dashboard.json` durch `scripts/update_dashboard.py` ausgeschlossen und
gelangen somit nicht in die öffentliche Dashboard-Datei.

Für die Veröffentlichung gilt bewusst eine offene Standardlogik:

-   `Internal` → nicht publizieren
-   `Public` → publizieren
-   kein Wert → publizieren

`Visibility` ist als organisationsweites Issue Field unter `awn-be`
definiert und an `Bug`, `Feature`, `Task` sowie Issues ohne Type angeheftet.
Dadurch steht das Feld repositoryübergreifend auch für zukünftige
WIS-BE-Repositories zur Verfügung.

## Übersetzungen

**Status**

-   `Blocked` → Blockiert
-   `Needs clarification` → Weitere Abklärungen nötig
-   `Todo` → Geplant
-   `In progress` → In Arbeit
-   `Ready to test` → Bereit zum Testen
-   `Done` → Erledigt
-   `Rejected` → Wird nicht umgesetzt

**Priority**

-   `Urgent` → Sehr hoch
-   `High` → Hoch
-   `Medium` → Mittel
-   `Low` → Niedrig

**Type**

-   `Bug` → Fehler
-   `Feature` → Funktion
-   `Task` → Aufgabe *(wird aktuell nicht verwendet)*

## Zusammenfassung, Filter und Sortierung

Die Zusammenfassung zeigt die Anzahl der Issues nach Bearbeitungsstatus:

-   Blockiert
-   Weitere Abklärungen nötig
-   Geplant
-   In Arbeit
-   Bereit zum Testen
-   Erledigt
-   Wird nicht umgesetzt
-   Nicht zugeordnet

Die angezeigten Zahlen berücksichtigen die aktuell gesetzten Filter.
`Nicht zugeordnet` macht Issues sichtbar, denen im konfigurierten
GitHub Project noch kein Status zugewiesen wurde.

Die öffentliche Dashboard-Anzeige kann nach **Typ**, **Priorität** und
**Status** gefiltert werden. Die Filter lassen sich miteinander kombinieren;
es werden nur Einträge angezeigt, die alle ausgewählten Kriterien erfüllen.

Die Einträge können zusätzlich über die Spaltenüberschriften nach **Thema**,
**Beschreibung**, **Typ**, **Priorität** und **Status** auf- oder absteigend
sortiert werden.

Die Filterung und Sortierung erfolgen direkt im Browser und verändern weder
die GitHub Issues noch die Daten in `dashboard.json`.

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
-   Keine Repository-Berechtigungen erforderlich, da die verwendeten
    GitHub Issues aus öffentlichen Repositories gelesen werden.

Der Fine-grained Personal Access Token ist zeitlich begrenzt und muss
vor Ablauf erneuert werden. Der aktuell verwendete Token läuft am
**31. August 2027** ab.

Der Token ist im Dashboard-Repository unter
**Settings → Secrets and variables → Actions** als Repository Secret
`DASHBOARD_TOKEN` hinterlegt.

Nach der Regeneration des Tokens muss dort der neue Token-Wert
eingetragen werden. Anschliessend sollte der Workflow
**Update dashboard** einmal manuell ausgeführt werden, um den Zugriff
zu prüfen.

> Der Token ist weder Bestandteil von `index.html` noch von
> `dashboard.json`. Er steht ausschliesslich der GitHub Action als
> Secret zur Verfügung.

## 3. GitHub Action

Der Workflow **Update dashboard** erzeugt `dashboard.json`. Er führt
`scripts/update_dashboard.py` aus und schreibt Änderungen an
`dashboard.json` zurück in das Repository.

Der Workflow kann auf zwei Arten starten:

**Automatisch, einmal pro Nacht.** GitHub führt geplante Workflows ohne
Zeitgarantie aus. Beobachtet wurden Verzögerungen von bis zu 5 Stunden
sowie ganz ausgefallene Auslöser. Der Workflow enthält deshalb vier
Auslöser pro Nacht (00:17, 01:41, 03:23 und 04:47 Uhr, `Europe/Zurich`).
Der erste, der startet, aktualisiert das Dashboard. Die übrigen erkennen
im Schritt «Watchdog», dass `dashboard.json` bereits vom selben Tag
stammt, und beenden sich nach wenigen Sekunden ohne Commit. Unter
**Actions** erscheinen daher bis zu vier Läufe pro Nacht, davon drei
sehr kurze.

**Manuell, jederzeit.** Über **Actions → Update dashboard → Run workflow**
lässt sich das Dashboard sofort aktualisieren, zum Beispiel nach
wichtigen Änderungen an Issues oder zur Kontrolle nach Anpassungen am
Skript. Manuelle Läufe werden vom Watchdog nie übersprungen. Sie
beeinflussen die automatische Aktualisierung der folgenden Nacht nicht.

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

## 5. Neue Repository-Sektion ergänzen

Für einen zusätzlichen WIS-BE-Prozess mit eigener Dashboard-Sektion werden
ein GitHub Repository und ein zugehöriges GitHub Project für die
Sprintplanung benötigt.

### GitHub Project vorbereiten

Im zugehörigen GitHub Project müssen die für das Dashboard verwendeten
Statuswerte eingerichtet werden.

Die Statuswerte sind Project-spezifisch und müssen deshalb bei jeder neuen
Sprintplanung einmal angelegt bzw. angepasst werden:

| Status | Farbe | Beschreibung |
| --- | --- | --- |
| `Blocked` | Pink | This is currently blocked by a dependency |
| `Needs clarification` | Gelb | This requires further clarification before work can continue |
| `Todo` | Grau | This item hasn't been started |
| `In progress` | Rot | This is actively being worked on |
| `Ready to test` | Grün | This is ready for testing |
| `Done` | Blau | This has been completed |
| `Rejected` | Violett | This will not be implemented |

`Todo` wird als **Default-Status** verwendet.

Die Bezeichnungen der Statuswerte müssen mit den in `config.json`
verwendeten Werten übereinstimmen, damit sie vom Dashboard korrekt erkannt
und übersetzt werden können.

### Visibility

Das organisationsweite Issue Field `Visibility` muss für neue Repositories
oder Projects **nicht separat eingerichtet werden**.

Es ist zentral in der Organisation `awn-be` definiert und steht dadurch
repositoryübergreifend auch für zukünftige WIS-BE-Prozesse zur Verfügung.
Das Feld ist an `Bug`, `Feature`, `Task` sowie Issues ohne Type angeheftet.

Für die Veröffentlichung im Dashboard gilt:

-   `Internal` → nicht publizieren
-   `Public` → publizieren
-   kein Wert → publizieren

### Dashboard-Konfiguration ergänzen

Anschliessend muss `config.json` um das entsprechende Repository und
GitHub Project erweitert werden, z. B.:

``` json
{
  "repo": "vertigis_planungsgrundlagen",
  "title": "Planungsgrundlagen",
  "project_number": 8,
  "project_title": "Sprintplanung Planungsgrundlagen"
}
```

Das Repository bestimmt die Dashboard-Sektion; das konfigurierte GitHub
Project liefert den dazugehörigen Bearbeitungsstatus.

Beim nächsten Lauf der GitHub Action wird die neue Sektion automatisch in
`dashboard.json` aufgenommen und im öffentlichen Dashboard angezeigt.

## KI-Unterstützung

Dieses Repository und das WIS-BE Dashboard wurden mit Unterstützung von
**ChatGPT (OpenAI; bei der aktuellen Umsetzung: GPT-5.6 Sol)** konzipiert
und umgesetzt.

Die KI-Unterstützung wurde insbesondere bei der Konzeption der Architektur,
der Entwicklung und Überarbeitung von Python-, HTML-, CSS- und
JavaScript-Code sowie bei der technischen Dokumentation eingesetzt.

Die fachlichen Anforderungen, Entscheidungen, Tests und die Freigabe der
Umsetzung erfolgten durch die Projektverantwortlichen.
