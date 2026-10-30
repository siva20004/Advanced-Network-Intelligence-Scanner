import socket
from concurrent.futures import ThreadPoolExecutor

def scan_port(target, port):
    try:
        sock = socket.socket()
        sock.settimeout(1)
        sock.connect((target, port))

        try:
            banner = sock.recv(1024).decode(errors="ignore").strip()
        except:
            banner = "No Banner"

        sock.close()

        return {
            "port": port,
            "banner": banner
        }

    except:
        return None


def scan_ports(target, port_list):
    results = []

    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(scan_port, target, port) for port in port_list]

        for future in futures:
            result = future.result()
            if result:
                results.append(result)

    return results
