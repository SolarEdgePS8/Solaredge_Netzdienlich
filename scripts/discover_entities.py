#!/usr/bin/env python3
import json
import os
import urllib.request

token = os.environ.get("SUPERVISOR_TOKEN")
if not token:
    raise SystemExit("SUPERVISOR_TOKEN fehlt. Im Home-Assistant-Terminal ausführen.")

req = urllib.request.Request(
    "http://supervisor/core/api/states",
    headers={"Authorization": f"Bearer {token}"},
)
with urllib.request.urlopen(req, timeout=30) as response:
    states = json.loads(response.read().decode())

def show(title, predicate):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)
    rows = []
    for item in states:
        entity = item.get("entity_id", "")
        state = item.get("state", "")
        attrs = item.get("attributes", {})
        if predicate(entity, state, attrs):
            rows.append((entity, state, attrs.get("unit_of_measurement", ""), attrs.get("device_class", "")))
    for row in sorted(rows)[:250]:
        print(f"{row[0]:70} state={row[1]:16} unit={row[2]:8} class={row[3]}")

show(
    "Kandidaten: aktuelle Leistung in W/kW",
    lambda e, s, a: a.get("device_class") == "power" or a.get("unit_of_measurement") in ["W", "kW"],
)
show(
    "Kandidaten: Energie in kWh – nur für Prognose-/Tagesenergie-Mappings",
    lambda e, s, a: a.get("unit_of_measurement") == "kWh",
)
show(
    "Kandidaten: Akku-SoE / Prozent",
    lambda e, s, a: a.get("unit_of_measurement") == "%" and any(x in e.lower() for x in ["battery", "b1", "soe", "soc", "reserve"]),
)
show(
    "Weather-Entities",
    lambda e, s, a: e.startswith("weather."),
)
show(
    "Beschreibbare Number-Entities mit SolarEdge/Battery/Storage",
    lambda e, s, a: e.startswith("number.") and any(x in e.lower() for x in ["solaredge", "battery", "storage", "reserve"]),
)
