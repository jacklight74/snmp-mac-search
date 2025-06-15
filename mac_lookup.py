import os

OUI_FILE = "oui.txt"
oui_dict = {}

def load_oui():
    if not os.path.exists(OUI_FILE):
        return

    with open(OUI_FILE, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if "(hex)" in line:
                parts = line.strip().split("(hex)")
                prefix = parts[0].strip().replace("-", ":").lower()
                vendor = parts[1].strip()
                oui_dict[prefix] = vendor

def get_vendor(mac: str):
    if not oui_dict:
        load_oui()
    prefix = mac.upper()[0:8].replace("-", ":")
    return oui_dict.get(prefix.lower(), "Unknown")