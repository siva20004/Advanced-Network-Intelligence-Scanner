# Advanced Network Intelligence Scanner

A modular Python platform for local network reconnaissance, risk assessment, CVE intelligence, report generation, and a live web dashboard. Designed for authorized security testing and lab use.

## Key Capabilities
- Auto-detect local network and discover hosts via ARP
- Multi-threaded TCP port scanning with custom port ranges
- Service banner grabbing and device-type identification
- CVE lookup through NVD keyword search
- Risk scoring (Low/Medium/High) plus per-port weighting
- Topology visualization (NetworkX + Matplotlib)
- Persistent scan history in SQLite with exportable HTML/JSON reports
- Modern Flask dashboard: KPIs, filters (High, Medium, Open Ports, CVE), copy-to-clipboard cards, delete-all, responsive layout

## Project Structure
```
Advanced-Network-Intelligence-Scanner/
+-- main.py                 # CLI entrypoint
+-- scanner.py              # port scanning
+-- host_discovery.py       # ARP discovery
+-- device_identifier.py    # device heuristics
+-- risk_analyzer.py        # risk scoring
+-- cve_lookup.py           # NVD lookup
+-- topology_visualizer.py  # graph rendering
+-- report_generator.py     # JSON/HTML reports
+-- database.py             # SQLite helpers
+-- dashboard.py            # Flask UI
+-- templates/
    +-- dashboard.html      # (legacy template, current UI in dashboard.py)
+-- requirements.txt
+-- reports/
    +-- json/               # generated JSON reports
    +-- html/               # generated HTML reports
```

## Installation
```bash
pip install -r requirements.txt
```

## Usage
- Auto mode (full LAN)
  ```bash
  sudo python main.py --auto
  # Windows: run in elevated shell for ARP
  ```
  - Scan single target
  ```bash
  python main.py -t 192.168.1.10
  ```
- Scan with custom ports
  ```bash
  python main.py -t 192.168.1.10 -p 22,80,443
  ```


## Dashboard
```bash
python dashboard.py
# browse http://127.0.0.1:5000
```

> **Note**: The dashboard at `localhost` works until a new program execution starts. After a scan finishes, you must restart `dashboard.py` to view the updated results.

Features: KPI cards, filters (High/Medium/Open Ports/CVE), copy card info, delete-all scans, responsive layout, no-cache rendering.

## Outputs
- `reports/json/report_<ip>.json`
- `reports/html/report_<ip>.html`
- `network_topology.png`
- `scan_history.db` (SQLite)

## Risk Scoring (examples)
- FTP (21): +3
- Telnet (23): +5
- RDP (3389): +4
- SMB (445): +4
Levels: 0-4 Low, 5-9 Medium, 10+ High.

## Ethical Use
For educational labs and authorized assessments only. Unauthorized scanning is illegal.

## Author
PALAPARTHI SIVA
2300032952@kluniversity.in