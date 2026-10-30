import json
from datetime import datetime
from pathlib import Path

REPORTS_DIR = Path("reports")
JSON_REPORTS_DIR = REPORTS_DIR / "json"
HTML_REPORTS_DIR = REPORTS_DIR / "html"


def _ensure_report_dirs():
    JSON_REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    HTML_REPORTS_DIR.mkdir(parents=True, exist_ok=True)

def generate_json_report(target, data):
    _ensure_report_dirs()
    filename = JSON_REPORTS_DIR / f"report_{target}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    return str(filename)


def generate_html_report(target, data):
    _ensure_report_dirs()
    filename = HTML_REPORTS_DIR / f"report_{target}.html"

    html = f"""
    <html>
    <body>
    <h1>Scan Report for {target}</h1>
    <p>Generated: {datetime.now()}</p>
    <h2>Risk: {data['risk_level']} ({data['risk_score']})</h2>
    <ul>
    """

    for port in data["open_ports"]:
        html += f"<li>Port {port['port']} - {port['banner']} - CVE: {port.get('cve')}</li>"

    html += "</ul></body></html>"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)

    return str(filename)
