import requests
import re
import time
import logging

# Simple in-memory cache to avoid duplicate API requests during a single scan run
_cve_cache = {}

# Offline fallback for common known vulnerable services (e.g., Metasploitable 2)
# This prevents NVD rate limits from completely breaking the scan experience
OFFLINE_CVE_DB = {
    "vsFTPd 2.3.4": "CVE-2011-2523",
    "UnrealIRCd 3.2.8.1": "CVE-2010-2075",
    "Samba 3.0.20": "CVE-2007-2447",
    "OpenSSH 4.7p1": "CVE-2008-5161",
    "ProFTPD 1.3.1": "CVE-2007-3146",
    "ProFTPD 1.3.5": "CVE-2015-3306",
    "Bind 9.4.2": "CVE-2008-0122",
    "Apache Tomcat/Coyote": "CVE-2010-2227",
    "distcc v1": "CVE-2004-2687",
    "drb ruby": "CVE-2011-2686"
}

def clean_banner(banner):
    if not banner or banner == "No Banner":
        return ""
        
    c = re.sub(r'^\d+\s+', '', banner)
    c = re.sub(r'^SSH-\d\.\d-', '', c)
    c = c.replace('(', '').replace(')', '').replace('_', ' ')
    
    words = [w for w in c.split() if w.strip()]
    
    noise = {'esmtp', 'ubuntu', 'debian', 'metasploitable', 'localdomain', 'ready', 'server', 'protocol', 'ftp'}
    filtered = []
    
    for w in words:
        if w.lower() not in noise and not w.lower().endswith('.localdomain'):
            filtered.append(w)
            
    if len(filtered) >= 2:
        return f"{filtered[0]} {filtered[1]}"
    elif len(filtered) == 1:
        return filtered[0]
        
    return ""

def lookup_cve(service_banner):
    if not service_banner or service_banner == "No Banner":
        return None

    keyword = clean_banner(service_banner)
    if not keyword:
        return None
        
    # 1. Try offline database first
    for known_service, cve_id in OFFLINE_CVE_DB.items():
        if known_service.lower() in keyword.lower() or keyword.lower() in known_service.lower():
            return cve_id
            
    # 2. Try cache
    if keyword in _cve_cache:
        return _cve_cache[keyword]

    # 3. Fallback to NVD API
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json"
    }

    try:
        url = f"https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch={keyword}"
        response = requests.get(url, headers=headers, timeout=6)
        
        if response.status_code == 200:
            data = response.json()
            if "vulnerabilities" in data and data["vulnerabilities"]:
                cve_id = data["vulnerabilities"][0]["cve"]["id"]
                _cve_cache[keyword] = cve_id
                time.sleep(1)  # Throttle for NVD API
                return cve_id
        elif response.status_code in [403, 429, 503]:
            # Rate limit hit, back off. DO NOT cache None!
            time.sleep(4)
            return None # Return None temporarily without caching
            
    except Exception as e:
        pass

    _cve_cache[keyword] = None
    return None

