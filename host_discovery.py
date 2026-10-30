from scapy.all import ARP, Ether, srp

def arp_scan(network):
    if not network:
        return []

    try:
        arp = ARP(pdst=network)
        ether = Ether(dst="ff:ff:ff:ff:ff:ff")
        packet = ether / arp

        result = srp(packet, timeout=2, verbose=0)[0]

        devices = []
        for sent, received in result:
            devices.append({
                "ip": received.psrc,
                "mac": received.hwsrc
            })

        return devices
    except Exception as e:
        print(f"[!] ARP scan error: {e}")
        return []

