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

MANIFEST = Path("/share/se_nf_release_audit_v295/release_manifest.txt")
REPORT_DIR = Path("/share/se_nf_release_audit_reports")
RUN = datetime.now().strftime("%Y%m%d_%H%M%S_manifest")
RUN_DIR = REPORT_DIR / RUN
RUN_DIR.mkdir(parents=True, exist_ok=True)

BAD = {"unknown", "unavailable", "none", "None", ""}

CRITICAL_KEYWORDS = [
    "charge_limit", "target", "desired", "pv_now", "pv_surplus",
    "battery_charge", "forecast", "load", "sql", "coverage",
    "weather", "planned", "start", "writer", "safety", "soc", "soe",
    "needed", "required", "energy", "session",
]

LEGACY_FORBIDDEN_MAIN = [
    "sensor.se_nf_forecast_pv_now",
    "sensor.se_nf_good_day_for_late_start",
    "sensor.se_nf_effective_available_pv_for_battery",
    "sensor.se_nf_effective_pv_delta",
]

def api_get(path):
    req = urllib.request.Request(API + path, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=15) as r:
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
        for m in re.finditer(pat, text):
            refs.add(m.group(1).strip())

    for line in text.splitlines():
        s = line.strip()
        if s.startswith("entity_id:"):
            val = s.split("entity_id:", 1)[1].strip().strip("'\"")
            if re.match(r"^[a-zA-Z0-9_]+\.[a-zA-Z0-9_]+$", val):
                refs.add(val)
        elif s.startswith("- "):
            val = s[2:].strip().strip("'\"")
            if re.match(r"^[a-zA-Z0-9_]+\.[a-zA-Z0-9_]+$", val):
                refs.add(val)
    return refs

def classify(eid):
    if eid in [
        "input_boolean.se_netzdienlich_enabled",
        "input_boolean.se_netzdienlich_debug",
        "sensor.speicher_ziel_ladestand",
    ]:
        return "PACKAGE_INTERNAL"
    if eid.startswith(("sensor.se_nf", "binary_sensor.se_nf", "input_boolean.se_nf", "input_number.se_nf", "input_select.se_nf", "input_text.se_nf", "input_datetime.se_nf")):
        return "PACKAGE_INTERNAL"
    if eid.startswith(("number.solaredge", "sensor.solaredge", "select.solaredge", "switch.solaredge")):
        return "REQUIRED_SOLAREDGE"
    if eid.startswith(("sensor.evcc", "binary_sensor.evcc", "switch.evcc")):
        return "OPTIONAL_EVCC"
    if eid.startswith("weather."):
        return "LOCAL_WEATHER_MAPPING"
    if eid.startswith(("sensor.power_", "sensor.energy_", "sensor.pv_")):
        return "LOCAL_POWER_PV_MAPPING"
    if eid.startswith(("sensor.wp_", "sensor.se_akku_preis")):
        return "OPTIONAL_OTHER_PACKAGE"
    return "EXTERNAL_UNKNOWN"

def main():
    states = state_map()

    files = []
    for line in MANIFEST.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        files.append(Path(line))

    out = []
    out.append("=== SE NF MANIFEST RELEASE AUDIT ===")
    out.append("Zeit: " + datetime.now().isoformat())
    out.append("Manifest: " + str(MANIFEST))
    out.append("Run dir: " + str(RUN_DIR))
    out.append("")

    all_text = ""
    refs_by_file = {}

    out.append("=== FILES ===")
    missing_files = 0
    for f in files:
        if not f.exists():
            out.append(f"FAIL: fehlt: {f}")
            missing_files += 1
            continue
        txt = f.read_text(errors="ignore")
        all_text += "\n" + txt
        refs_by_file[f] = extract_refs(txt)
        out.append(f"PASS: {f} | {len(txt.splitlines())} lines")
    out.append("")

    out.append("=== FORBIDDEN LEGACY REFERENCES ===")
    legacy_hits = []
    for legacy in LEGACY_FORBIDDEN_MAIN:
        if legacy in all_text:
            legacy_hits.append(legacy)
            out.append("FAIL: " + legacy)
    if not legacy_hits:
        out.append("PASS: keine verbotenen Legacy-Referenzen im Release-Manifest")
    out.append("")

    out.append("=== UNIQUE_ID DUPLICATES IN MANIFEST ===")
    unique = {}
    for f in files:
        if not f.exists():
            continue
        for i, line in enumerate(f.read_text(errors="ignore").splitlines(), 1):
            m = re.search(r"unique_id:\s*['\"]?([^'\"\s#]+)", line)
            if m:
                unique.setdefault(m.group(1), []).append((f, i))
    dups = {k:v for k,v in unique.items() if len(v) > 1}
    if not dups:
        out.append("PASS: keine duplicate unique_id im Manifest")
    else:
        for k,v in dups.items():
            out.append("FAIL: duplicate unique_id " + k)
            for f,i in v:
                out.append(f"  {f}:{i}")
    out.append("")

    all_refs = {}
    for f, refs in refs_by_file.items():
        for r in refs:
            all_refs.setdefault(r, set()).add(f)

    critical = []
    orange = []
    external = []

    out.append("=== REFERENCED ENTITIES ===")
    for eid, fs in sorted(all_refs.items()):
        st = states.get(eid, {}).get("state", "missing")
        cat = classify(eid)
        bad = st == "missing" or str(st) in BAD
        crit = any(k in eid.lower() for k in CRITICAL_KEYWORDS)

        if cat == "PACKAGE_INTERNAL" and bad and crit:
            critical.append((eid, st, fs))
        elif cat == "PACKAGE_INTERNAL" and bad:
            orange.append((eid, st, fs))
        elif cat not in ["PACKAGE_INTERNAL"]:
            external.append((eid, st, cat, fs))

        mark = " BAD" if bad else ""
        out.append(f"{cat:24} | {eid:65} | {str(st):18}{mark}")

    out.append("")
    out.append("=== PACKAGE-INTERNAL BAD REFERENCES ===")
    out.append("critical_internal: " + str(len(critical)))
    for eid, st, fs in critical:
        out.append(f"ROT: {eid} = {st} | files=" + ",".join(f.name for f in fs))
    out.append("orange_internal: " + str(len(orange)))
    for eid, st, fs in orange:
        out.append(f"ORANGE: {eid} = {st} | files=" + ",".join(f.name for f in fs))

    out.append("")
    out.append("=== EXTERNAL / PORTABILITY MAPPINGS ===")
    for eid, st, cat, fs in external:
        out.append(f"{cat}: {eid} = {st} | files=" + ",".join(f.name for f in fs))

    out.append("")
    out.append("=== RELEASE GATE ===")
    gate_fail = missing_files or legacy_hits or dups or critical
    out.append("missing_files: " + str(missing_files))
    out.append("legacy_hits: " + str(len(legacy_hits)))
    out.append("duplicate_unique_ids: " + str(len(dups)))
    out.append("critical_internal: " + str(len(critical)))
    out.append("GATE_MANIFEST: " + ("FAIL" if gate_fail else "PASS_OR_EXTERNAL_REVIEW"))

    report = RUN_DIR / "manifest_release_audit.txt"
    report.write_text("\n".join(out) + "\n")
    print("\n".join(out))
    print()
    print("Report:", report)

if __name__ == "__main__":
    main()
