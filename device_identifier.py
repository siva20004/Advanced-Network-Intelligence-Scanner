def identify_device(ip, open_ports, gateway_ip):
    ports = [p["port"] for p in open_ports]

    if ip == gateway_ip:
        return "Router"

    if 9100 in ports:
        return "Printer"

    if 3389 in ports:
        return "Windows Machine"

    if 22 in ports and 80 in ports:
        return "Linux Server"

    if 80 in ports or 443 in ports:
        return "Web Server"

    return "Unknown Device"
