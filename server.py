from fastapi import FastAPI, Query, HTTPException
from tortoise.contrib.fastapi import register_tortoise
from models import Router
from snmpfunc import get_router_info, get_arp_table, snmp_get
import uvicorn
from mac_lookup import get_vendor

app = FastAPI(title="Router SNMP Tracker")

@app.post("/router")
async def add_router(name: str, ip: str, snmp_user: str, snmp_pass: str):
    fake_router = Router(name=name, ip=ip, snmp_user=snmp_user, snmp_pass=snmp_pass)
    snmp_response = snmp_get(fake_router, "1.3.6.1.2.1.1.5.0")

    if snmp_response == "N/A":
        raise HTTPException(status_code=400, detail="SNMP Timeout or invalid credentials")

    router = await Router.create(name=name, ip=ip, snmp_user=snmp_user, snmp_pass=snmp_pass)
    return {"status": "created", "id": router.id, "sysName": snmp_response}

@app.get("/routers")
async def list_routers():
    routers = await Router.all()
    return [get_router_info(router) for router in routers]

@app.get("/find-mac", summary="MAC 일부로 검색 (제조사 포함)")
async def find_mac(mac: str = Query(..., description="MAC 주소 일부 (예: 00:11 또는 11:22:33)")):
    mac = mac.lower().replace("-", ":")
    routers = await Router.all()
    found = []

    for router in routers:
        arp_list = get_arp_table(router)
        for entry in arp_list:
            if mac in entry["mac"]:
                found.append({
                    "router_name": router.name,
                    "router_ip": router.ip,
                    "device_ip": entry["ip"],
                    "mac": entry["mac"],
                    "vendor": get_vendor(entry["mac"])
                })

    return {"mac_input": mac, "matched": found}

@app.get("/devices", summary="모든 공유기에서 연결된 디바이스 전체 조회")
async def get_all_devices():
    routers = await Router.all()
    all_devices = []

    for router in routers:
        arp_table = get_arp_table(router)
        for entry in arp_table:
            all_devices.append({
                "router_name": router.name,
                "router_ip": router.ip,
                "device_ip": entry["ip"],
                "mac": entry["mac"],
                "vendor": get_vendor(entry["mac"])
            })

    return {"count": len(all_devices), "devices": all_devices}

register_tortoise(
    app,
    db_url='sqlite://routers.db',
    modules={'models': ['models']},
    generate_schemas=True,
    add_exception_handlers=True
)

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)