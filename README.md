# WIS-BE Dashboard

Saubere Trennung von **interner Issue-Pflege** (GitHub) und
**öffentlicher Anzeige** (WIS-BE Homepage):

```text
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

Die GitHub-Daten werden automatisch in `dashboard.json` aufbereitet und
von der öffentlichen Seite ausschliesslich aus dieser Datei geladen.
Dadurch greift die öffentliche Anzeige **nicht direkt auf die GitHub
API** zu.

## Dateien

- `index.html` -- öffentliche, responsive Anzeige
- `dashboard.json` -- automatisch erzeugte Dashboard-Daten
- `config.json` -- Repository-/Project-Zuordnung und Übersetzungen
- `scripts/update_dashboard.py` -- liest GitHub aus und erzeugt
    `dashboard.json`
- `.github/workflows/update-dashboard.yml` -- automatische tägliche
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

Über das organisationsweite GitHub Issue Field `Visibility` wird
gesteuert, welche Issues in das öffentliche WIS-BE Dashboard übernommen
werden.

Das Feld ist als Single-Select-Feld mit folgenden Werten definiert:

- `Public` → wird im öffentlichen Dashboard angezeigt
- `Internal` → wird nicht ins öffentliche Dashboard übernommen

Issues mit `Visibility = Internal` werden bereits beim Erzeugen von
`dashboard.json` durch `scripts/update_dashboard.py` ausgeschlossen und
gelangen somit nicht in die öffentliche Dashboard-Datei.

Für die Veröffentlichung gilt bewusst eine offene Standardlogik:

- `Internal` → nicht publizieren
- `Public` → publizieren
- kein Wert → publizieren

`Visibility` ist als organisationsweites Issue Field unter `awn-be`
definiert und an `Bug`, `Feature`, `Task` sowie Issues ohne Type
angeheftet. Dadurch steht das Feld repositoryübergreifend auch für
zukünftige WIS-BE-Repositories zur Verfügung.

## Übersetzungen

**Status**

- `Blocked` → Blockiert
- `Needs clarification` → Weitere Abklärungen nötig
- `Todo` → Geplant
- `In progress` → In Arbeit
- `Ready to test` → Bereit zum Testen
- `Done` → Erledigt
- `Rejected` → Wird nicht umgesetzt

**Priority**

- `Urgent` → Sehr hoch
- `High` → Hoch
- `Medium` → Mittel
- `Low` → Niedrig

**Type**

- `Bug` → Fehler
- `Feature` → Funktion
- `Task` → Aufgabe *(wird aktuell nicht verwendet)*

## Zusammenfassung, Filter, Sortierung und Darstellung

Die Zusammenfassung zeigt die Anzahl der Issues nach Bearbeitungsstatus:

- Blockiert
- Weitere Abklärungen nötig
- Geplant
- In Arbeit
- Bereit zum Testen
- Erledigt
- Wird nicht umgesetzt
- Nicht zugeordnet

Die angezeigten Zahlen berücksichtigen die aktuell gesetzten Filter.
`Nicht zugeordnet` macht Issues sichtbar, denen im konfigurierten GitHub
Project noch kein Status zugewiesen wurde.

Die öffentliche Dashboard-Anzeige kann nach **Typ**, **Priorität** und
**Status** gefiltert werden. Die Filter lassen sich miteinander
kombinieren; es werden nur Einträge angezeigt, die alle ausgewählten
Kriterien erfüllen.

Die Einträge können zusätzlich über die Spaltenüberschriften nach
**Thema**, **Beschreibung**, **Typ**, **Priorität**, **Status**,
**Eingang** und **Erledigt** auf- oder absteigend sortiert werden.

### Eingangs- und Erledigungsdatum

Für jedes Issue werden zwei Datumsangaben aus GitHub übernommen:

- **Eingang** basiert auf `created_at` und entspricht dem
    Erstellungsdatum des GitHub Issues.
- **Erledigt** basiert auf `closed_at` und entspricht dem Zeitpunkt,
    an dem das GitHub Issue geschlossen wurde. Bei offenen Issues wird
    `–` angezeigt.

Das Erledigungsdatum wird bewusst aus dem tatsächlichen GitHub-Status
des Issues abgeleitet und nicht aus dem Project-Status `Done`.

### Responsive Darstellung

Bei ausreichend breiter Darstellung werden die Issues als Tabelle mit
den Spalten **Thema**, **Beschreibung**, **Typ**, **Priorität**,
**Status**, **Eingang** und **Erledigt** angezeigt.

Bei schmalerer Darstellung wechselt das Dashboard automatisch auf eine
Card-Ansicht, damit die Tabellenspalten nicht abgeschnitten oder
überlagert werden. Die Card-Ansicht enthält ebenfalls Eingangs- und
Erledigungsdatum.

Die konkreten Breakpoints und die dafür relevante Portal-Einbettung sind
unter **4. GitHub Pages → Einbindung in ArcGIS Portal** dokumentiert.

### Ein- und ausklappbare Prozessbereiche

Die einzelnen Dashboard-Sektionen sind ein- und ausklappbar und beim
ersten Laden standardmässig **eingeklappt**. Dadurch bleibt die
Übersicht auch bei einer wachsenden Zahl von WIS-BE-Prozessen kompakt.

Der Eintragszähler neben jeder Prozessüberschrift berücksichtigt die
aktuell gesetzten Filter. Das Ein- oder Ausklappen einer Sektion
verändert weder die Filterung noch die Zahlen in der Zusammenfassung.
Der gewählte Klappzustand bleibt auch bei Filter- und Sortieränderungen
erhalten.

Filterung, Sortierung und Klappzustand werden ausschliesslich im Browser
verarbeitet und verändern weder die GitHub Issues noch die Daten in
`dashboard.json`.

------------------------------------------------------------------------

# Technische Einrichtung und Betrieb

Die folgenden Abschnitte dokumentieren die technische Einrichtung und
den laufenden Betrieb des WIS-BE Dashboards. Sie dienen insbesondere als
Referenz für Wartung, Fehleranalyse und die Erweiterung um zusätzliche
WIS-BE-Prozesse.

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

- Organization permission: **Projects -- Read-only**
- Keine Repository-Berechtigungen erforderlich, da die verwendeten
    GitHub Issues aus öffentlichen Repositories gelesen werden.

Der Fine-grained Personal Access Token ist zeitlich begrenzt und muss
vor Ablauf erneuert werden. Der aktuell verwendete Token läuft am **31.
August 2027** ab.

Der Token ist im Dashboard-Repository unter **Settings → Secrets and
variables → Actions** als Repository Secret `DASHBOARD_TOKEN`
hinterlegt.

Nach der Regeneration des Tokens muss dort der neue Token-Wert
eingetragen werden. Anschliessend sollte der Workflow **Update
dashboard** einmal manuell ausgeführt werden, um den Zugriff zu prüfen.

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

**Manuell, jederzeit.** Über **Actions → Update dashboard → Run
workflow** lässt sich das Dashboard sofort aktualisieren, zum Beispiel
nach wichtigen Änderungen an Issues oder zur Kontrolle nach Anpassungen
am Skript. Manuelle Läufe werden vom Watchdog nie übersprungen. Sie
beeinflussen die automatische Aktualisierung der folgenden Nacht nicht.

## 4. GitHub Pages

Nach erfolgreicher Datenübernahme wurde GitHub Pages für das Dashboard
aktiviert.

Unter **Settings → Pages → Build and deployment** wurden folgende
Einstellungen verwendet:

- Source: `Deploy from a branch`
- Branch: `main`
- Folder: `/ (root)`

Das Dashboard ist dadurch unter folgender Adresse erreichbar:

`https://awn-be.github.io/wis-be-dashboard/`

Diese GitHub-Pages-Seite wird per iFrame in ArcGIS Portal eingebunden.

### Einbindung in ArcGIS Portal

Das Dashboard wird auf der WIS-BE-Seite als iFrame eingebunden.

Die iFrame-Card belegt mit `width: 12` die gesamte verfügbare Breite der
Portal-Zeile. Zusätzlich wird für die Portal-Sektion eine breite
Darstellung verwendet. Diese Einstellung ist wichtig, weil eine feste
bzw. schmalere Section den iFrame auf Desktop-Bildschirmen so stark
begrenzen kann, dass das Dashboard unnötig früh in die Card-Ansicht
wechselt.

Für die responsive Darstellung gelten derzeit folgende Stufen:

- Ab `1300px` steht genügend Platz für die vollständige Tabelle mit
    sieben Spalten zur Verfügung.
- Unterhalb von `1300px` wechselt das Dashboard automatisch auf die
    Card-Ansicht.
- Unterhalb von `900px` wird zusätzlich die Statusübersicht von vier
    auf zwei Spalten reduziert.
- Unterhalb von `560px` greift die Darstellung für sehr schmale
    Bildschirmbreiten.

Damit bleibt auf breiten Desktop-Ansichten die tabellarische Darstellung
erhalten, während kleinere Fenster und mobile Geräte weiterhin responsiv
dargestellt werden.

Für den iFrame werden derzeit folgende Einstellungen verwendet:

- Höhe: `800px`
- Scrollbar: aktiviert
- Breite der Card: `12` (volle Zeilenbreite)
- Portal-Sektion: breite Darstellung

## 5. Neue Repository-Sektion ergänzen

Für einen zusätzlichen WIS-BE-Prozess mit eigener Dashboard-Sektion
werden ein GitHub Repository und ein zugehöriges GitHub Project für die
Sprintplanung benötigt.

### GitHub Project vorbereiten

Im zugehörigen GitHub Project müssen die für das Dashboard verwendeten
Statuswerte eingerichtet werden.

Die Statuswerte sind Project-spezifisch und müssen deshalb bei jeder
neuen Sprintplanung einmal angelegt bzw. angepasst werden:

  -----------------------------------------------------------------------
  Status                  Farbe                   Beschreibung
  ----------------------- ----------------------- -----------------------
  `Blocked`               Pink                    This is currently
                                                  blocked by a dependency

  `Needs clarification`   Gelb                    This requires further
                                                  clarification before
                                                  work can continue

  `Todo`                  Grau                    This item hasn't been
                                                  started

  `In progress`           Rot                     This is actively being
                                                  worked on

  `Ready to test`         Grün                    This is ready for
                                                  testing

  `Done`                  Blau                    This has been completed

  `Rejected`              Violett                 This will not be
                                                  implemented
  -----------------------------------------------------------------------

`Todo` wird als **Default-Status** verwendet.

Die Bezeichnungen der Statuswerte müssen mit den in `config.json`
definierten englischen Statusbezeichnungen übereinstimmen, damit sie vom
Dashboard korrekt erkannt und übersetzt werden können.

### Visibility

Das organisationsweite Issue Field `Visibility` muss für neue
Repositories oder Projects **nicht separat eingerichtet werden**.

Es ist zentral in der Organisation `awn-be` definiert und steht dadurch
repositoryübergreifend auch für zukünftige WIS-BE-Prozesse zur
Verfügung. Das Feld ist an `Bug`, `Feature`, `Task` sowie Issues ohne
Type angeheftet.

Für die Veröffentlichung im Dashboard gilt:

- `Internal` → nicht publizieren
- `Public` → publizieren
- kein Wert → publizieren

### Dashboard-Konfiguration ergänzen

Anschliessend muss `config.json` um das entsprechende Repository und
GitHub Project erweitert werden, z. B.:

```json
{
  "repo": "vertigis_planungsgrundlagen",
  "title": "Planungsgrundlagen",
  "project_number": 8,
  "project_title": "Sprintplanung Planungsgrundlagen"
}
```

Das Repository bestimmt die Dashboard-Sektion; das konfigurierte GitHub
Project liefert den dazugehörigen Bearbeitungsstatus.

Beim nächsten Lauf der GitHub Action wird die neue Sektion automatisch
in `dashboard.json` aufgenommen und im öffentlichen Dashboard angezeigt.
Neue Sektionen sind in der öffentlichen Anzeige beim ersten Laden
automatisch eingeklappt.

## KI-Unterstützung

Dieses Repository und das WIS-BE Dashboard wurden mit Unterstützung von
**ChatGPT (OpenAI; bei der aktuellen Umsetzung: GPT-5.6 Sol)**
konzipiert und umgesetzt.

Die KI-Unterstützung wurde insbesondere bei der Konzeption der
Architektur, der Entwicklung und Überarbeitung von Python-, HTML-, CSS-
und JavaScript-Code sowie bei der technischen Dokumentation eingesetzt.

Die fachlichen Anforderungen, Entscheidungen, Tests und die Freigabe der
Umsetzung erfolgten durch die Projektverantwortlichen.
