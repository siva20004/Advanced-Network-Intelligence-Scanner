from flask import Flask, render_template_string, request, redirect, url_for, make_response, jsonify
import sqlite3
import json
from datetime import datetime
from database import DB_PATH, init_db, get_scan_count, hard_reset_database

app = Flask(__name__)

DASHBOARD_TEMPLATE = """
<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Network Intelligence Dashboard</title>
  <link rel=\"preconnect\" href=\"https://fonts.googleapis.com\">
  <link rel=\"preconnect\" href=\"https://fonts.gstatic.com\" crossorigin>
  <link href=\"https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700;800&family=IBM+Plex+Mono:wght@400;500&display=swap\" rel=\"stylesheet\">
  <style>
    :root {
      --bg: #0a1016;
      --surface: #111b25;
      --surface-2: #152332;
      --text: #eaf4ff;
      --muted: #9db1c7;
      --accent: #44d1b4;
      --danger: #ff6a6a;
      --warn: #ffb14a;
      --low: #6dd08b;
      --border: rgba(201, 221, 245, 0.18);
      --glow: rgba(68, 209, 180, 0.25);
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      color: var(--text);
      font-family: \"Sora\", sans-serif;
      background:
        radial-gradient(1200px 600px at 10% -10%, rgba(68, 209, 180, 0.2), transparent 60%),
        radial-gradient(1000px 500px at 100% 0%, rgba(85, 145, 255, 0.12), transparent 60%),
        linear-gradient(180deg, #091018 0%, #0a1016 100%);
      min-height: 100vh;
    }

    .shell {
      width: min(1200px, 94vw);
      margin: 28px auto;
      padding: 24px;
      background: linear-gradient(180deg, rgba(17, 27, 37, 0.9), rgba(11, 18, 27, 0.95));
      border: 1px solid var(--border);
      border-radius: 20px;
      backdrop-filter: blur(7px);
      box-shadow: 0 20px 50px rgba(0, 0, 0, 0.35);
    }

    .head {
      display: flex;
      justify-content: space-between;
      gap: 18px;
      align-items: flex-start;
      flex-wrap: wrap;
      margin-bottom: 22px;
    }

    .title {
      margin: 0;
      font-size: clamp(1.5rem, 4vw, 2.4rem);
      letter-spacing: 0.01em;
    }

    .subtitle {
      margin: 10px 0 0;
      color: var(--muted);
      font-size: 0.96rem;
      max-width: 700px;
      line-height: 1.5;
    }

    .stamp {
      font-family: \"IBM Plex Mono\", monospace;
      color: #c8d9eb;
      background: rgba(9, 17, 25, 0.8);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 10px 12px;
      font-size: 0.82rem;
      white-space: nowrap;
    }

    .db-hint {
      margin-top: 10px;
      color: var(--muted);
      font-family: \"IBM Plex Mono\", monospace;
      font-size: 0.74rem;
      word-break: break-all;
    }

    .kpis {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
      gap: 12px;
      margin-bottom: 24px;
    }

    .kpi {
      background: linear-gradient(160deg, var(--surface), var(--surface-2));
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 14px;
      position: relative;
      overflow: hidden;
    }

    .kpi::after {
      content: \"\";
      position: absolute;
      inset: -30% auto auto -30%;
      width: 90px;
      height: 90px;
      background: radial-gradient(circle, var(--glow), transparent 70%);
      pointer-events: none;
    }

    .kpi .label {
      color: var(--muted);
      font-size: 0.82rem;
      margin-bottom: 6px;
    }

    .kpi .value {
      font-size: 1.5rem;
      font-weight: 700;
    }

    .section-title {
      margin: 4px 0 12px;
      font-size: 1rem;
      color: #c6d8eb;
    }

    .controls {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      flex-wrap: wrap;
      margin-bottom: 14px;
    }

    .filters {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }

    .btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      border-radius: 10px;
      border: 1px solid var(--border);
      padding: 8px 12px;
      font-size: 0.8rem;
      font-weight: 700;
      letter-spacing: 0.03em;
      text-decoration: none;
      color: #d8e9fb;
      background: rgba(16, 27, 40, 0.8);
      cursor: pointer;
      transition: 0.2s ease;
    }

    .btn:hover { border-color: rgba(201, 221, 245, 0.45); }
    .btn.active { background: rgba(68, 209, 180, 0.18); border-color: rgba(68, 209, 180, 0.5); color: #bfffee; }
    .btn-danger { background: rgba(255, 106, 106, 0.14); border-color: rgba(255, 106, 106, 0.45); color: #ffdada; }
    .notice {
      margin-bottom: 12px;
      border: 1px solid rgba(68, 209, 180, 0.4);
      background: rgba(68, 209, 180, 0.12);
      color: #c9fff2;
      border-radius: 10px;
      padding: 10px 12px;
      font-size: 0.85rem;
    }

    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: 14px;
    }

    .scan {
      border: 1px solid var(--border);
      background: linear-gradient(180deg, #111b26, #0f1824);
      border-radius: 14px;
      padding: 14px;
    }

    .scan-top {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      margin-bottom: 10px;
      flex-wrap: wrap;
    }

    .target {
      font-family: \"IBM Plex Mono\", monospace;
      font-size: 1.03rem;
      letter-spacing: 0.03em;
    }

    .badge {
      padding: 4px 10px;
      border-radius: 999px;
      font-size: 0.74rem;
      font-weight: 700;
      letter-spacing: 0.04em;
      border: 1px solid transparent;
    }

    .risk-high { color: #ffd5d5; background: rgba(255, 106, 106, 0.16); border-color: rgba(255, 106, 106, 0.6); }
    .risk-medium { color: #ffe6c2; background: rgba(255, 177, 74, 0.16); border-color: rgba(255, 177, 74, 0.52); }
    .risk-low { color: #d9f9e3; background: rgba(109, 208, 139, 0.16); border-color: rgba(109, 208, 139, 0.45); }
    .status-open { color: #b8fff0; background: rgba(68, 209, 180, 0.14); border-color: rgba(68, 209, 180, 0.45); }
    .btn-copy { margin-left: 6px; padding: 4px 8px; font-size: 0.72rem; }

    .meta {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 8px;
      margin-bottom: 12px;
    }

    .meta div {
      background: rgba(9, 16, 24, 0.8);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 8px;
    }

    .meta .m-label {
      color: var(--muted);
      font-size: 0.72rem;
      margin-bottom: 4px;
      text-transform: uppercase;
      letter-spacing: 0.06em;
    }

    .meta .m-value {
      font-size: 0.9rem;
      word-break: break-word;
    }

    .ports {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-top: 8px;
    }

    .port {
      font-family: \"IBM Plex Mono\", monospace;
      font-size: 0.72rem;
      background: rgba(68, 209, 180, 0.12);
      color: #b8fff0;
      border: 1px solid rgba(68, 209, 180, 0.35);
      border-radius: 8px;
      padding: 4px 8px;
    }

    .empty {
      border: 1px dashed var(--border);
      border-radius: 14px;
      padding: 24px;
      text-align: center;
      color: var(--muted);
      background: rgba(13, 20, 30, 0.6);
    }

    @media (max-width: 980px) {
      .kpis { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .grid { grid-template-columns: 1fr; }
    }

    @media (max-width: 560px) {
      .shell { margin: 14px auto; padding: 16px; border-radius: 16px; }
      .kpis { grid-template-columns: 1fr; }
      .meta { grid-template-columns: 1fr; }
      .stamp { width: 100%; text-align: center; }
      .controls { align-items: stretch; }
    }
  </style>
</head>
<body>
  <main class=\"shell\">
    <header class=\"head\">
      <div>
        <h1 class=\"title\">Network Intelligence Dashboard</h1>
        <p class=\"subtitle\">Live visibility of discovered hosts, exposed services, and risk posture from persisted scanner history.</p>
        <div class=\"db-hint\">DB: {{ db_path }} | Rows: {{ db_rows }}</div>
      </div>
      <div class=\"stamp\">Generated {{ generated_at }}</div>
    </header>

    <section class=\"kpis\">
      <article class=\"kpi\">
        <div class=\"label\">Total Scans</div>
        <div class=\"value\">{{ total_scans }}</div>
      </article>
      <article class=\"kpi\">
        <div class=\"label\">Unique Targets</div>
        <div class=\"value\">{{ unique_targets }}</div>
      </article>
      <article class=\"kpi\">
        <div class=\"label\">High Risk Findings</div>
        <div class=\"value\">{{ high_risk_count }}</div>
      </article>
      <article class=\"kpi\">
        <div class=\"label\">Medium Risk Findings</div>
        <div class=\"value\">{{ medium_risk_count }}</div>
      </article>
      <article class=\"kpi\">
        <div class=\"label\">Open Ports Observed</div>
        <div class=\"value\">{{ open_ports_total }}</div>
      </article>
    </section>

    <div class=\"controls\">
      <div class=\"filters\">
        <a href=\"{{ url_for('home') }}\" class=\"btn {% if active_filter == 'ALL' %}active{% endif %}\">All</a>
        <a href=\"{{ url_for('home', risk='HIGH') }}\" class=\"btn {% if active_filter == 'HIGH' %}active{% endif %}\">High Risk</a>
        <a href=\"{{ url_for('home', risk='MEDIUM') }}\" class=\"btn {% if active_filter == 'MEDIUM' %}active{% endif %}\">Medium Risk</a>
        <a href=\"{{ url_for('home', open_only='1') }}\" class=\"btn {% if active_filter == 'OPEN' %}active{% endif %}\">Open Ports</a>
        <a href=\"{{ url_for('home', cve_only='1') }}\" class=\"btn {% if active_filter == 'CVE' %}active{% endif %}\">CVE</a>
      </div>
      <button type=\"button\" class=\"btn btn-danger\" onclick=\"deleteScans()\">Delete All Scans</button>
    </div>

    {% if delete_notice %}
      <div class=\"notice\">{{ delete_notice }}</div>
    {% endif %}

    <h2 class=\"section-title\">Recent Scan Results{% if active_filter != 'ALL' %} ({{ active_filter }}){% endif %}</h2>

    {% if scans %}
      <section class=\"grid\">
        {% for scan in scans %}
          <article class=\"scan\">
            <div class=\"scan-top\">
              <div class=\"target\">{{ scan.target }}</div>
              <div>
                <span class=\"badge {{ scan.risk_class }}\">{{ scan.risk_level }}</span>
                {% if scan.has_open_ports %}
                  <span class=\"badge status-open\">OPEN</span>
                {% endif %}
                <button class=\"btn btn-copy\" onclick=\"copyScan({{ loop.index0 }})\">Copy</button>
              </div>
            </div>

            <div class=\"meta\">
              <div>
                <div class=\"m-label\">Timestamp</div>
                <div class=\"m-value\">{{ scan.timestamp_display }}</div>
              </div>
              <div>
                <div class=\"m-label\">Device Type</div>
                <div class=\"m-value\">{{ scan.device_type }}</div>
              </div>
              <div>
                <div class=\"m-label\">Risk Score</div>
                <div class=\"m-value\">{{ scan.risk_score }}</div>
              </div>
            </div>

{% if scan.open_ports %}
              <div class=\"ports\">
                {% for port in scan.open_ports %}
                  <span class=\"port\">{{ port.port }} | {{ port.banner }}{% if port.cve %} | CVE: {{ port.cve }}{% endif %}</span>
                {% endfor %}
              </div>
            {% else %}
              <div class=\"m-value\" style=\"color: var(--muted);\">No open ports recorded.</div>
            {% endif %}
          </article>
        {% endfor %}
      </section>
    {% else %}
      <div class=\"empty\">No scan records found in <code>scan_history.db</code>.</div>
    {% endif %}
  </main>
</body>
<script>
  async function deleteScans() {
    if (!confirm('Delete all scan history? This cannot be undone.')) return;
    try {
      const res = await fetch('{{ url_for("delete_scans") }}', { method: 'POST' });
      if (!res.ok) {
        const msg = await res.text();
        alert('Delete failed: ' + msg);
        return;
      }
      window.location = '{{ url_for("home") }}';
    } catch (err) {
      alert('Delete failed: ' + err);
    }
  }

  const SCANS = {{ scans | tojson }};

  function copyScan(idx) {
    const s = SCANS[idx];
    if (!s) return;
    const ports = (s.open_ports || []).map(p => {
      const parts = [`port ${p.port}`, p.banner];
      if (p.cve) parts.push(`CVE ${p.cve}`);
      return parts.join(' | ');
    });
    const lines = [
      `Target: ${s.target}`,
      `Risk: ${s.risk_level} (${s.risk_score})`,
      `Device: ${s.device_type}`,
      `Timestamp: ${s.timestamp_display}`,
      `Open Ports:`,
      ...(ports.length ? ports : ['None'])
    ];
    const text = lines.join('\\n');
    navigator.clipboard.writeText(text).catch(err => alert('Copy failed: ' + err));
  }
</script>
</html>
"""


def _load_json(value):
    try:
        data = json.loads(value)
        if isinstance(data, dict):
            return data
    except (TypeError, json.JSONDecodeError):
        pass
    return {}


def _format_timestamp(value):
    try:
        return datetime.fromisoformat(value).strftime("%Y-%m-%d %H:%M:%S")
    except (TypeError, ValueError):
        return value or "N/A"


def _get_db_connection():
    return sqlite3.connect(str(DB_PATH), timeout=10)


@app.route("/")
def home():
    risk_filter = str(request.args.get("risk", "")).upper()
    open_only = request.args.get("open_only") == "1"
    cve_only = request.args.get("cve_only") == "1"
    deleted_value = request.args.get("deleted")
    delete_notice = None
    if deleted_value is not None:
        delete_notice = f"Deleted {deleted_value} scan record(s)."

    rows = []
    db_rows = 0
    try:
        init_db()
        conn = _get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT target, result, timestamp FROM scans ORDER BY timestamp DESC")
        rows = cursor.fetchall()
        conn.close()
        db_rows = len(rows)
    except sqlite3.Error:
        rows = []

    scans = []
    total_open_ports = 0

    for target, result_json, timestamp in rows:
        data = _load_json(result_json)
        open_ports = data.get("open_ports") if isinstance(data.get("open_ports"), list) else []

        normalized_ports = []
        for port in open_ports:
            if isinstance(port, dict):
                cve = port.get("cve")
                normalized_ports.append(
                    {
                        "port": port.get("port", "?"),
                        "banner": port.get("banner", "Unknown")[:50],
                        "cve": cve if cve not in (None, "", "None") else None,
                    }
                )

        risk_level = str(data.get("risk_level", "UNKNOWN")).upper()
        risk_class = "risk-low"
        if risk_level == "HIGH":
            risk_class = "risk-high"
        elif risk_level == "MEDIUM":
            risk_class = "risk-medium"

        scans.append(
            {
                "target": target,
                "timestamp_display": _format_timestamp(timestamp),
                "device_type": data.get("device_type", "Unknown"),
                "risk_score": data.get("risk_score", 0),
                "risk_level": risk_level,
                "risk_class": risk_class,
                "open_ports": normalized_ports,
                "has_open_ports": len(normalized_ports) > 0,
            }
        )
        total_open_ports += len(normalized_ports)

    filtered_scans = scans
    active_filter = "ALL"
    if risk_filter in {"HIGH", "MEDIUM"}:
        filtered_scans = [scan for scan in scans if scan["risk_level"] == risk_filter]
        active_filter = risk_filter
    elif open_only:
        filtered_scans = [scan for scan in scans if scan["has_open_ports"]]
        active_filter = "OPEN"
    elif cve_only:
        filtered_scans = [scan for scan in scans if any(p.get("cve") for p in scan["open_ports"])]
        active_filter = "CVE"

    html = render_template_string(
        DASHBOARD_TEMPLATE,
        scans=filtered_scans,
        total_scans=len(scans),
        unique_targets=len({scan["target"] for scan in scans}),
        high_risk_count=sum(1 for scan in scans if scan["risk_level"] == "HIGH"),
        medium_risk_count=sum(1 for scan in scans if scan["risk_level"] == "MEDIUM"),
        open_ports_total=total_open_ports,
        active_filter=active_filter,
        delete_notice=delete_notice,
        db_path=str(DB_PATH),
        db_rows=db_rows,
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )
    response = make_response(html)
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@app.route("/delete-scans", methods=["POST"])
def delete_scans():
    try:
        before_count = get_scan_count()
        hard_reset_database()
        after_count = get_scan_count()
        if after_count != 0:
            return f"Failed to clear scan history. Rows still present: {after_count}", 500
    except sqlite3.Error as exc:
        return f"Failed to delete scans: {exc}", 500
    except PermissionError as exc:
        return f"Failed to reset database file: {exc}", 500
    return jsonify({"deleted": before_count})


if __name__ == "__main__":
    app.run(debug=True)
