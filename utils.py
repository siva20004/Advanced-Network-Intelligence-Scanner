import socket
import psutil
import ipaddress

def parse_ports(port_input):
    ports = set()
    parts = [p.strip() for p in str(port_input).split(",") if p.strip()]

    for part in parts:
        if "-" in part:
            try:
                start, end = map(int, part.split("-", 1))
                ports.update(range(start, end + 1))
            except ValueError:
                continue
        else:
            try:
                ports.add(int(part))
            except ValueError:
                continue

    return sorted([p for p in ports if 1 <= p <= 65535])


def get_default_gateway():
    """
    Robustly determine the default gateway IP without brittle external C-dependencies.
    Primary: Scapy routing table (cross-platform).
    Fallback: netifaces (if installed and supported).
    """
    # 1. Try Scapy routing table
    try:
        from scapy.all import conf
        route = conf.route.route("0.0.0.0")
        gw = route[2]
        if gw and gw != "0.0.0.0":
            return gw
    except Exception:
        pass

    # 2. Try netifaces if available and implemented
    try:
        import netifaces
        gateways = netifaces.gateways()
        default = gateways.get("default")
        if default and netifaces.AF_INET in default:
            return default[netifaces.AF_INET][0]
    except Exception:
        pass

    return None


def get_local_network():
    """
    Determines the active local network CIDR (e.g. 192.168.1.0/24),
    avoiding loopback (127.x.x.x) and APIPA link-local (169.254.x.x) virtual interfaces.
    """
    local_ip = None

    # Step 1: Detect active local IP from default route
    try:
        from scapy.all import conf
        local_ip = conf.route.route("0.0.0.0")[1]
    except Exception:
        pass

    if not local_ip or local_ip.startswith("127.") or local_ip.startswith("169.254."):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                local_ip = s.getsockname()[0]
        except Exception:
            pass

    # Step 2: Match local IP to psutil interface to get the exact netmask
    interfaces = psutil.net_if_addrs()
    if local_ip:
        for interface, addrs in interfaces.items():
            for addr in addrs:
                if addr.family == socket.AF_INET and addr.address == local_ip:
                    netmask = addr.netmask or "255.255.255.0"
                    network = ipaddress.IPv4Network(f"{local_ip}/{netmask}", strict=False)
                    return str(network)

    # Step 3: Fallback scan through psutil interfaces ignoring loopback and link-local
    for interface, addrs in interfaces.items():
        for addr in addrs:
            if addr.family == socket.AF_INET:
                ip = addr.address
                if not ip.startswith("127.") and not ip.startswith("169.254."):
                    netmask = addr.netmask or "255.255.255.0"
                    network = ipaddress.IPv4Network(f"{ip}/{netmask}", strict=False)
                    return str(network)

    return None
