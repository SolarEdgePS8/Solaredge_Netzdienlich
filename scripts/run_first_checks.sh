#!/bin/sh
set -eu
: "${SUPERVISOR_TOKEN:?SUPERVISOR_TOKEN fehlt}"
API="http://supervisor/core/api"

for entity in \
  sensor.se_nf_config_check \
  sensor.se_nf_sanity_check \
  sensor.se_nf_writer_mode \
  sensor.se_nf_charge_limit_target \
  sensor.se_nf_desired_target \
  sensor.se_nf_charge_limit_actual \
  sensor.se_nf_soe_age_s \
  sensor.se_nf_charge_limit_age_s \
  sensor.se_nf_today_charge_window \
  sensor.se_nf_decision_reason \
  input_boolean.se_netzdienlich_enabled
do
  echo
  echo "### $entity"
  curl -fsS \
    -H "Authorization: Bearer $SUPERVISOR_TOKEN" \
    "$API/states/$entity"
done

echo
echo "Hinweis: writer_mode=normal kann gültig sein. Config Check und Sanity Check müssen vor Aktivierung ok sein."

# ISSUE #4 + #5 – optionale Mappings und Zeitfensterdiagnose
python3 - <<'PY'
import json
import os
import urllib.request

API = "http://supervisor/core/api"
HEADERS = {"Authorization": f"Bearer {os.environ['SUPERVISOR_TOKEN']}"}
BAD = {"", "unknown", "unavailable", "none", "null"}
ENERGY = {"Wh", "kWh", "MWh"}


def get(entity_id):
    request = urllib.request.Request(f"{API}/states/{entity_id}", headers=HEADERS)
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return json.load(response)
    except Exception:
        return None


def state(entity_id):
    item = get(entity_id)
    return str(item.get("state", "not_found")) if item else "not_found"


def energy_ok(entity_id):
    item = get(entity_id)
    if not item:
        return False
    try:
        float(item.get("state"))
    except (TypeError, ValueError):
        return False
    return item.get("attributes", {}).get("unit_of_measurement") in ENERGY


print("\n=== OPTIONALE MAPPINGS ===")
source = state("sensor.se_nf_adaptive_pv_actual_today_source")
kind = (get("sensor.se_nf_adaptive_pv_actual_today_source") or {}).get("attributes", {}).get("source_kind")
print("ACTUAL_PV_TODAY_ENTITIES:", kind or "optional_inactive", "| source=", source)

daily = state("input_text.se_nf_daily_consumption_entity").strip()
print("DAILY_CONSUMPTION_ENTITY:", "ACTIVE" if energy_ok(daily) else "OPTIONAL_INACTIVE / MANUAL_FALLBACK", "| entity=", daily)

meter = state("input_text.se_nf_pv_actual_meter_source_entity").strip()
print("PV_ACTUAL_METER_SOURCE_ENTITY:", "ACTIVE" if energy_ok(meter) else "OPTIONAL_INACTIVE / INVALID_MAPPING", "| entity=", meter)

evcc = get("binary_sensor.se_nf_evcc_grid_charge_request") or {}
evcc_attrs = evcc.get("attributes", {})
print("EVCC_BATTERY_MODE_ENTITY:", evcc_attrs.get("mapping_status", "optional_inactive"), "| entity=", evcc_attrs.get("source_entity", ""), "| raw=", evcc_attrs.get("raw_mode", ""))

print("\n=== ZEITFENSTER ===")
window = get("sensor.se_nf_today_charge_window") or {}
attrs = window.get("attributes", {})
print("state=", window.get("state"))
print("window_valid=", attrs.get("window_valid"))
print("start=", attrs.get("start_timestamp"), "end=", attrs.get("end_timestamp"))
print("source=", attrs.get("selected_start_source"), "session=", attrs.get("session_state"))
PY

