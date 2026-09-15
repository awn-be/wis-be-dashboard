#!/usr/bin/env python3
"""
Erzeugt dashboard.json aus:
- öffentlichen GitHub Issues
- Issue-Feld "Priority"
- GitHub Projects v2 #6 / #7 für "Status"

Nur Python-Standardbibliothek.
"""
from __future__ import annotations
import json, os, re, sys, urllib.request, urllib.error
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
TOKEN = os.environ.get("DASHBOARD_TOKEN") or os.environ.get("GH_TOKEN")
API_VERSION = "2026-03-10"

def request_json(url: str, *, method="GET", data=None, auth=True):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "wis-be-dashboard",
        "X-GitHub-Api-Version": API_VERSION,
    }
    if auth and TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    body = None if data is None else json.dumps(data).encode("utf-8")
    req = urllib.request.Request(url, data=body, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{method} {url} -> HTTP {e.code}: {detail[:500]}") from e

def graphql(query: str, variables: dict):
    if not TOKEN:
        raise RuntimeError(
            "Für GitHub Projects wird DASHBOARD_TOKEN benötigt. "
            "Lege den Token als Repository Secret DASHBOARD_TOKEN an."
        )
    result = request_json(
        "https://api.github.com/graphql",
        method="POST",
        data={"query": query, "variables": variables},
        auth=True,
    )
    if result.get("errors"):
        raise RuntimeError("GitHub GraphQL: " + json.dumps(result["errors"], ensure_ascii=False))
    return result["data"]

def strip_markdown(text: str) -> str:
    text = re.sub(r"```[\s\S]*?```", " ", text or "")
    text = re.sub(r"<img\b[^>]*>", " ", text, flags=re.I)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"!\[[^\]]*\]\([^)]+\)", " ", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.M)
    text = re.sub(r"[*_~>#]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def extract_section(body: str, headings: list[str]) -> str:
    """
    Extrahiert einen Abschnitt aus dem Issue-Body.
    Unterstützt fett formatierte Abschnittstitel (**Titel**)
    sowie Markdown-Überschriften (## Titel).
    """
    if not body:
        return ""

    lines = body.splitlines()
    start = None

    for i, line in enumerate(lines):
        clean = line.strip()

        # Markdown-Formatierung des Titels entfernen
        clean = re.sub(r"^#{1,6}\s*", "", clean)
        clean = re.sub(r"^\*\*(.*?)\*\*$", r"\1", clean)
        clean = clean.strip()

        if clean.lower() in [h.lower() for h in headings]:
            start = i + 1
            break

    if start is None:
        return ""

    content = []

    for line in lines[start:]:
        clean = line.strip()

        # Nächster fett formatierter Abschnittstitel
        if re.match(r"^\*\*.+\*\*$", clean):
            break

        # Oder nächste Markdown-Überschrift
        if re.match(r"^#{1,6}\s+", clean):
            break

        content.append(line)

    return strip_markdown("\n".join(content))

def extract_behaviors(body: str):
    current_behavior = extract_section(
        body,
        ["Momentanes Verhalten", "Aktuelles Verhalten"]
    )

    expected_behavior = extract_section(
        body,
        ["Erwartetes Verhalten"]
    )

    return current_behavior, expected_behavior

def extract_description(body: str) -> str:
    if not body:
        return "Keine Beschreibung hinterlegt."

    current_behavior, expected_behavior = extract_behaviors(body)

    parts = []

    if current_behavior:
        parts.append(f"Momentanes Verhalten: {current_behavior}")

    if expected_behavior:
        parts.append(f"Erwartetes Verhalten: {expected_behavior}")

    # Fallback für Issues ohne diese beiden Abschnitte
    text = " ".join(parts) if parts else strip_markdown(body)

    return text[:317].rstrip() + "…" if len(text) > 320 else text

def list_issues(org: str, repo: str):
    # Aktuell reichen <100 Issues pro Repo. Pagination ist trotzdem eingebaut.
    items, page = [], 1

    while True:
        url = (
            f"https://api.github.com/repos/{org}/{repo}/issues"
            f"?state=all&per_page=100&page={page}&sort=updated&direction=desc"
        )

        batch = request_json(url, auth=bool(TOKEN))

        print(
            f"{org}/{repo}: API-Seite {page} -> "
            f"{len(batch)} Einträge vor PR-Filter"
        )

        issues = [x for x in batch if "pull_request" not in x]

        print(
            f"{org}/{repo}: API-Seite {page} -> "
            f"{len(issues)} Issues nach PR-Filter"
        )

        items.extend(issues)

        # Pagination anhand der ungefilterten API-Antwort beurteilen.
        if len(batch) < 100:
            break

        page += 1

    print(f"{org}/{repo}: insgesamt {len(items)} Issues")
    return items

def issue_priority(org: str, repo: str, number: int):
    url = f"https://api.github.com/repos/{org}/{repo}/issues/{number}/issue-field-values?per_page=100"
    fields = request_json(url, auth=bool(TOKEN))
    for f in fields:
        if (f.get("issue_field_name") or "").lower() == "priority":
            raw = ((f.get("single_select_option") or {}).get("name")
                   or (f.get("value") if isinstance(f.get("value"), str) else None))
            return raw
    return None

PROJECT_QUERY = r"""
query($org:String!, $number:Int!, $cursor:String) {
  organization(login:$org) {
    projectV2(number:$number) {
      title
      items(first:100, after:$cursor) {
        pageInfo { hasNextPage endCursor }
        nodes {
          content {
            ... on Issue {
              number
              repository { nameWithOwner }
            }
          }
          fieldValues(first:50) {
            nodes {
              ... on ProjectV2ItemFieldSingleSelectValue {
                name
                field {
                  ... on ProjectV2FieldCommon { name }
                }
              }
            }
          }
        }
      }
    }
  }
}
"""

def project_statuses(org: str, project_number: int):
    statuses = {}
    cursor = None
    project_title = None
    while True:
        data = graphql(PROJECT_QUERY, {"org": org, "number": project_number, "cursor": cursor})
        project = (data.get("organization") or {}).get("projectV2")
        if not project:
            raise RuntimeError(f"Project #{project_number} in Organisation {org} nicht gefunden.")
        project_title = project.get("title")
        connection = project["items"]
        for node in connection["nodes"]:
            content = node.get("content") or {}
            repo = ((content.get("repository") or {}).get("nameWithOwner"))
            number = content.get("number")
            if not repo or not number:
                continue
            raw_status = None
            for fv in (node.get("fieldValues") or {}).get("nodes", []):
                field = fv.get("field") or {}
                if field.get("name") == "Status":
                    raw_status = fv.get("name")
                    break
            statuses[(repo, number)] = raw_status
        page = connection["pageInfo"]
        if not page["hasNextPage"]:
            break
        cursor = page["endCursor"]
    return project_title, statuses

def issue_type(issue):
    raw = issue.get("type")

    if isinstance(raw, dict):
        raw = raw.get("name")

    if isinstance(raw, str) and raw:
        return raw

    return "Nicht zugeordnet"

def main():
    org = CONFIG["organization"]
    tr = CONFIG["translations"]
    sections = []

    for cfg in CONFIG["repositories"]:
        repo = cfg["repo"]
        project_number = cfg["project_number"]
        project_title, statuses = project_statuses(org, project_number)
        issues = list_issues(org, repo)
        rows = []

        for issue in issues:
            number = issue["number"]
            raw_priority = issue_priority(org, repo, number)
            raw_type = issue_type(issue)
            raw_status = statuses.get((f"{org}/{repo}", number))

            # Falls ein Issue noch nicht im Project liegt, transparent anzeigen.
            status_de = tr["status"].get(raw_status, "Nicht zugeordnet") if raw_status else "Nicht zugeordnet"

            body = issue.get("body") or ""
            current_behavior, expected_behavior = extract_behaviors(body)

            rows.append({
                "number": number,
                "title": issue["title"],
                "url": issue["html_url"],
                "description": extract_description(body),
                "current_behavior": current_behavior,
                "expected_behavior": expected_behavior,
                "type_raw": raw_type,
                "type": tr["type"].get(raw_type, raw_type),
                "priority_raw": raw_priority,
                "priority": tr["priority"].get(raw_priority, "Nicht zugeordnet"),
                "status_raw": raw_status,
                "status": status_de,
                "issue_state": issue.get("state"),
                "updated_at": issue.get("updated_at"),
            })

        # Sinnvolle Reihenfolge: Status, Priorität, Titel.
        status_order = {"In progress":0, "Ready to test":1, "Todo":2, None:3, "Done":4}
        priority_order = {"Urgent":0, "High":1, "Medium":2, "Low":3, None:4}
        rows.sort(key=lambda x: (
            status_order.get(x["status_raw"], 3),
            priority_order.get(x["priority_raw"], 4),
            x["title"].lower()
        ))

        sections.append({
            "id": repo,
            "title": cfg["title"],
            "project_number": project_number,
            "project_title": project_title or cfg.get("project_title"),
            "items": rows
        })

    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "GitHub",
        "prototype": False,
        "sections": sections
    }
    (ROOT / "dashboard.json").write_text(
        json.dumps(output, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8"
    )
    print(f"dashboard.json aktualisiert: {sum(len(x['items']) for x in sections)} Issues")

if __name__ == "__main__":
    main()
