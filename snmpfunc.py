import subprocess
import re

def snmp_get(router, oid):
    cmd = [
        "snmpget", "-v3", "-l", "authNoPriv",
        "-u", router.snmp_user, "-a", "MD5", "-A", router.snmp_pass,
        router.ip, oid
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return "N/A"
    return result.stdout.strip().split("= ")[-1]

def get_router_info(router):
    return {
        "name": router.name,
        "ip": router.ip,
        "sysName": snmp_get(router, "1.3.6.1.2.1.1.5.0"),
        "sysDescr": snmp_get(router, "1.3.6.1.2.1.1.1.0"),
        "sysLocation": snmp_get(router, "1.3.6.1.2.1.1.6.0"),
        "sysContact": snmp_get(router, "1.3.6.1.2.1.1.4.0"),
    }

def get_arp_table(router):
    cmd = [
        "snmpwalk", "-v3", "-l", "authNoPriv",
        "-u", router.snmp_user, "-a", "MD5", "-A", router.snmp_pass,
        router.ip, "1.3.6.1.2.1.4.22"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return []

    arp_entries = []
    for line in result.stdout.splitlines():
        match = re.match(r".*ipNetToMediaPhysAddress\.\d+\.(\d+\.\d+\.\d+\.\d+)\s+=\s+.*: (.+)", line)
        if match:
            ip_addr, mac_addr = match.groups()
            arp_entries.append({"ip": ip_addr, "mac": mac_addr.lower()})
    return arp_entries