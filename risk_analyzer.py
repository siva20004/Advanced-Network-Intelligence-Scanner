def calculate_risk(open_ports):
    risk_score = 0

    risky_ports = {
        21: 3,
        23: 5,
        3389: 4,
        445: 4,
        139: 3
    }

    for port in open_ports:
        if port["port"] in risky_ports:
            risk_score += risky_ports[port["port"]]

    if risk_score >= 10:
        level = "HIGH"
    elif risk_score >= 5:
        level = "MEDIUM"
    else:
        level = "LOW"

    return risk_score, level
