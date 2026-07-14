#!/usr/bin/env python3
import json
import os
import re
import urllib.request
from pathlib import Path
from datetime import datetime

API = "http://supervisor/core/api"
TOKEN = os.environ.get("SUPERVISOR_TOKEN")
HEADERS = {"Authorization": f"Bearer {TOKEN}"}
HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "release_manifest.txt"
REPORT_DIR = Path("/share/se_nf_release_audit_reports")
RUN = datetime.now().strftime("%Y%m%d_%H%M%S_manifest")
RUN_DIR = REPORT_DIR / RUN
RUN_DIR.mkdir(parents=True, exist_ok=True)

BAD = {"unknown", "unavailable", "none", "None", ""}
OPTIONAL_EMPTY_INTERNAL = {
    "input_text.se_nf_discharge_limit_entity",
}
CRITICAL_KEYWORDS = [
    "charge_limit", "target", "desired", "pv_now", "pv_surplus",
    "battery_charge", "forecast", "load", "sql", "coverage",
    "weather", "planned", "start", "writer", "safety", "soc", "soe",
    "needed", "required", "energy", "session", "discharge_limit",
]
LEGACY_FORBIDDEN = [
    "sensor.se_nf_forecast_pv_now",
    "sensor.se_nf_good_day_for_late_start",
    "sensor.se_nf_effective_available_pv_for_battery",
    "sensor.se_nf_effective_pv_delta",
]

def api_get(path):
    req = urllib.request.Request(API + path, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode())

def state_map():
    return {s["entity_id"]: s for s in api_get("/states")}

def extract_refs(text):
    refs = set()
    patterns = [
        r"states\(\s*['\"]([^'\"]+)['\"]\s*\)",
        r"is_state\(\s*['\"]([^'\"]+)['\"]\s*,",
        r"state_attr\(\s*['\"]([^'\"]+)['\"]\s*,",
        r"has_value\(\s*['\"]([^'\"]+)['\"]\s*\)",
    ]
    for pat in patterns:
        for match in re.finditer(pat, text):
            refs.add(match.group(1).strip())

    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("entity_id:"):
            value = stripped.split("entity_id:", 1)[1].strip().strip("'\"")
            if re.match(r"^[A-Za-z0-9_]+\.[A-Za-z0-9_]+$", value):
                refs.add(value)
        elif stripped.startswith("- "):
            value = stripped[2:].strip().strip("'\"")
            if re.match(r"^[A-Za-z0-9_]+\.[A-Za-z0-9_]+$", value):
                refs.add(value)
    return refs

def classify(entity_id):
    if entity_id in {
        "input_boolean.se_netzdienlich_enabled",
        "input_boolean.se_netzdienlich_debug",
        "sensor.speicher_ziel_ladestand",
    }:
        return "PACKAGE_INTERNAL"
    if entity_id.startswith((
        "sensor.se_nf", "binary_sensor.se_nf", "input_boolean.se_nf",
        "input_number.se_nf", "input_select.se_nf", "input_text.se_nf",
        "input_datetime.se_nf",
    )):
        return "PACKAGE_INTERNAL"
    if entity_id.startswith((
        "number.solaredge", "sensor.solaredge",
        "select.solaredge", "switch.solaredge",
    )):
        return "REQUIRED_SOLAREDGE"
    if entity_id.startswith(("sensor.evcc", "binary_sensor.evcc", "switch.evcc")):
        return "OPTIONAL_EVCC"
    if entity_id.startswith("weather."):
        return "LOCAL_WEATHER_MAPPING"
    if entity_id.startswith(("sensor.power_", "sensor.energy_", "sensor.pv_")):
        return "LOCAL_POWER_PV_MAPPING"
    return "EXTERNAL_UNKNOWN"

def main():
    if not TOKEN:
        raise SystemExit("SUPERVISOR_TOKEN fehlt. Im Home-Assistant-Terminal ausführen.")
    if not MANIFEST.exists():
        raise SystemExit(f"Manifest fehlt: {MANIFEST}")

    states = state_map()
    files = []
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            files.append(Path(line))

    out = [
        "=== SE NF MANIFEST RELEASE AUDIT ===",
        "Zeit: " + datetime.now().isoformat(),
        "Manifest: " + str(MANIFEST),
        "Run dir: " + str(RUN_DIR),
        "",
        "=== FILES ===",
    ]

    missing_files = 0
    texts = {}
    for path in files:
        if not path.exists():
            out.append(f"FAIL: fehlt: {path}")
            missing_files += 1
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        texts[path] = text
        out.append(f"PASS: {path} | {len(text.splitlines())} lines")

    all_text = "\n".join(texts.values())
    out += ["", "=== FORBIDDEN LEGACY REFERENCES ==="]
    legacy_hits = [entity for entity in LEGACY_FORBIDDEN if entity in all_text]
    if legacy_hits:
        for entity in legacy_hits:
            out.append("FAIL: " + entity)
    else:
        out.append("PASS: keine verbotenen Legacy-Referenzen im Release-Manifest")

    out += ["", "=== UNIQUE_ID DUPLICATES IN MANIFEST ==="]
    unique_ids = {}
    for path, text in texts.items():
        for line_no, line in enumerate(text.splitlines(), 1):
            match = re.search(r"unique_id:\s*['\"]?([^'\"\s#]+)", line)
            if match:
                unique_ids.setdefault(match.group(1), []).append((path, line_no))
    duplicates = {key: value for key, value in unique_ids.items() if len(value) > 1}
    if duplicates:
        for key, locations in sorted(duplicates.items()):
            out.append("FAIL: duplicate unique_id " + key)
            for path, line_no in locations:
                out.append(f"  {path}:{line_no}")
    else:
        out.append("PASS: keine duplicate unique_id im Manifest")

    refs_by_file = {}
    all_refs = {}
    for path, text in texts.items():
        refs = extract_refs(text)
        refs_by_file[path] = refs
        for entity in refs:
            all_refs.setdefault(entity, set()).add(path)

    critical = []
    orange = []
    optional_unconfigured = []
    external = []

    out += ["", "=== REFERENCED ENTITIES ==="]
    for entity, source_files in sorted(all_refs.items()):
        state = states.get(entity, {}).get("state", "missing")
        category = classify(entity)
        is_bad = state == "missing" or str(state) in BAD

        if entity in OPTIONAL_EMPTY_INTERNAL and is_bad:
            optional_unconfigured.append((entity, state, source_files))
            out.append(
                f"OPTIONAL_UNCONFIGURED     | {entity:65} | {str(state):18}"
            )
            continue

        critical_name = any(keyword in entity.lower() for keyword in CRITICAL_KEYWORDS)
        if category == "PACKAGE_INTERNAL" and is_bad and critical_name:
            critical.append((entity, state, source_files))
        elif category == "PACKAGE_INTERNAL" and is_bad:
            orange.append((entity, state, source_files))
        elif category != "PACKAGE_INTERNAL":
            external.append((entity, state, category, source_files))

        marker = " BAD" if is_bad else ""
        out.append(f"{category:24} | {entity:65} | {str(state):18}{marker}")

    out += ["", "=== PACKAGE-INTERNAL BAD REFERENCES ==="]
    out.append("critical_internal: " + str(len(critical)))
    for entity, state, source_files in critical:
        out.append(
            f"ROT: {entity} = {state} | files="
            + ",".join(sorted(path.name for path in source_files))
        )

    out.append("orange_internal: " + str(len(orange)))
    for entity, state, source_files in orange:
        out.append(
            f"ORANGE: {entity} = {state} | files="
            + ",".join(sorted(path.name for path in source_files))
        )

    out.append("optional_unconfigured: " + str(len(optional_unconfigured)))
    for entity, state, source_files in optional_unconfigured:
        out.append(
            f"OPTIONAL: {entity} = {state} | keine Release-Blockade | files="
            + ",".join(sorted(path.name for path in source_files))
        )

    out += ["", "=== OPTIONAL MAPPING TARGET CHECK ==="]
    discharge_helper = states.get(
        "input_text.se_nf_discharge_limit_entity", {}
    ).get("state", "")
    if discharge_helper in BAD or discharge_helper == "missing":
        out.append(
            "INFO: Discharge-Limit-Mapping ist leer. "
            "Das ist zulässig; der optionale Discharge-Reset bleibt deaktiviert."
        )
    else:
        target_state = states.get(discharge_helper, {}).get("state", "missing")
        if target_state == "missing" or str(target_state) in BAD:
            out.append(
                f"WARN: Discharge-Limit-Ziel {discharge_helper} = {target_state}. "
                "Optionales Mapping prüfen."
            )
        else:
            out.append(
                f"PASS: Discharge-Limit-Ziel {discharge_helper} = {target_state}"
            )

    out += ["", "=== EXTERNAL / PORTABILITY MAPPINGS ==="]
    for entity, state, category, source_files in external:
        out.append(
            f"{category}: {entity} = {state} | files="
            + ",".join(sorted(path.name for path in source_files))
        )

    gate_fail = bool(missing_files or legacy_hits or duplicates or critical)
    out += [
        "",
        "=== RELEASE GATE ===",
        "missing_files: " + str(missing_files),
        "legacy_hits: " + str(len(legacy_hits)),
        "duplicate_unique_ids: " + str(len(duplicates)),
        "critical_internal: " + str(len(critical)),
        "GATE_MANIFEST: " + ("FAIL" if gate_fail else "PASS_OR_EXTERNAL_REVIEW"),
    ]

    report = RUN_DIR / "manifest_release_audit.txt"
    report.write_text("\n".join(out) + "\n", encoding="utf-8")
    print("\n".join(out))
    print()
    print("Report:", report)

if __name__ == "__main__":
    main()
