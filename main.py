import argparse
from rich import print
from utils import parse_ports, get_local_network, get_default_gateway
from host_discovery import arp_scan
from scanner import scan_ports
from risk_analyzer import calculate_risk
from device_identifier import identify_device
from cve_lookup import lookup_cve
from topology_visualizer import generate_topology
from report_generator import generate_json_report, generate_html_report
from database import init_db, save_scan

import threading
from dashboard import app

def start_dashboard():
    # Run dashboard on port 5000 in background thread, without reloader
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)

def main():
    print("\n=== Intelligent Network Scanner ===")
    print("Auto scan local network : sudo python main.py --auto")
    print("Scan specific target    : python main.py -t <ip> [-p ports]")
    print("Made by: PALAPARTHI SIVA\n")

    parser = argparse.ArgumentParser(description="Advanced Network Intelligence Scanner")
    parser.add_argument("-t", "--target", help="Target IP")
    parser.add_argument("-p", "--ports", default="1-1024", help="Port range")
    parser.add_argument("--auto", action="store_true", help="Auto-detect local network")

    args = parser.parse_args()

    # Start the Dashboard silently in the background
    dashboard_thread = threading.Thread(target=start_dashboard, daemon=True)
    dashboard_thread.start()
    print("[bold green]Dashboard started in background at http://127.0.0.1:5000[/bold green]\n")

    init_db()
    port_list = parse_ports(args.ports)
    gateway_ip = get_default_gateway()

    if args.auto:
        network = get_local_network()
        if not network:
            print("[bold red]Error: Could not automatically detect local network.[/bold red]")
            return

        print(f"[yellow]Detected Network:[/yellow] {network}")

        devices = arp_scan(network)
        print(f"[green]Discovered {len(devices)} devices[/green]")

        discovered_ips = []

        for device in devices:
            ip = device["ip"]
            discovered_ips.append(ip)

            print(f"\n[bold cyan]Scanning {ip}[/bold cyan]")

            open_ports = scan_ports(ip, port_list)

            for port in open_ports:
                port["cve"] = lookup_cve(port["banner"])

            risk_score, risk_level = calculate_risk(open_ports)
            device_type = identify_device(ip, open_ports, gateway_ip)

            result = {
                "target": ip,
                "device_type": device_type,
                "open_ports": open_ports,
                "risk_score": risk_score,
                "risk_level": risk_level
            }

            save_scan(ip, result)
            generate_json_report(ip, result)
            generate_html_report(ip, result)

        generate_topology("Scanner", discovered_ips)
        print(f"\n[bold green]Network scan complete. Topology saved as network_topology.png[/bold green]")
        print("[cyan]Reports saved in reports/json/ and reports/html/[/cyan]")

    elif args.target:
        ip = args.target
        open_ports = scan_ports(ip, port_list)

        for port in open_ports:
            port["cve"] = lookup_cve(port["banner"])

        risk_score, risk_level = calculate_risk(open_ports)
        device_type = identify_device(ip, open_ports, gateway_ip)

        result = {
            "target": ip,
            "device_type": device_type,
            "open_ports": open_ports,
            "risk_score": risk_score,
            "risk_level": risk_level
        }

        save_scan(ip, result)
        generate_json_report(ip, result)
        generate_html_report(ip, result)
        print(f"\n[bold green]Scan completed for {ip}[/bold green]")
        print("[cyan]Reports saved in reports/json/ and reports/html/[/cyan]")

    else:
        print("Please specify --auto or -t target")

if __name__ == "__main__":
    main()
