#!/usr/bin/env python3
import json
import os
import re
import subprocess
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path

API = "http://supervisor/core/api"
TOKEN = os.environ.get("SUPERVISOR_TOKEN")
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
}

PACKAGE_DIR = Path("/config/packages")
MAIN = PACKAGE_DIR / "solaredge_netzdienlich.yaml"
REPORT_ROOT = Path("/share/se_nf_release_audit_reports")
RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S")
RUN_DIR = REPORT_ROOT / RUN_ID
RUN_DIR.mkdir(parents=True, exist_ok=True)

BAD = {"unknown", "unavailable", "none", "None", ""}

CORE_PREFIXES = (
    "sensor.se_nf",
    "binary_sensor.se_nf",
    "input_boolean.se_nf",
    "input_number.se_nf",
    "input_select.se_nf",
    "input_text.se_nf",
    "input_datetime.se_nf",
)

HELPER_PREFIXES = (
    "input_boolean.",
    "input_number.",
    "input_select.",
    "input_text.",
    "input_datetime.",
)

SOLAREDGE_PREFIXES = (
    "sensor.solaredge",
    "number.solaredge",
    "switch.solaredge",
    "select.solaredge",
)

OPTIONAL_PREFIXES = (
    "sensor.evcc",
    "binary_sensor.evcc",
    "switch.evcc",
    "sensor.wp_hochpreis",
    "sensor.se_akku_preis",
)

KNOWN_LEGACY_MUST_NOT_BE_IN_MAIN = [
    "sensor.se_nf_forecast_pv_now",
    "sensor.se_nf_good_day_for_late_start",
    "sensor.se_nf_effective_available_pv_for_battery",
    "sensor.se_nf_effective_pv_delta",
]

CRITICAL_KEYWORDS = [
    "charge_limit", "target", "desired", "pv_now", "pv_surplus",
    "battery_charge", "forecast", "load", "sql", "coverage",
    "weather", "planned", "start", "writer", "safety", "soc", "soe",
    "needed", "required", "energy", "session",
]

REQUIRED_CORE_ENTITIES = [
    "sensor.se_nf_config_check",
    "sensor.se_nf_sanity_check",
    "sensor.se_nf_today_charge_window",
    "sensor.se_nf_decision_reason",
    "sensor.se_nf_charge_limit_target",
    "sensor.se_nf_charge_limit_actual",
    "sensor.se_nf_desired_target",
    "sensor.se_nf_writer_mode",
    "sensor.se_nf_needed_energy",
    "sensor.se_nf_required_charge_minutes",
    "sensor.se_nf_today_planned_start_candidate_timestamp",
    "sensor.se_nf_active_planned_start_timestamp",
    "input_datetime.se_nf_session_planned_start",
    "sensor.se_nf_available_pv_for_battery_today",
    "sensor.se_nf_coverage_ratio",
    "sensor.se_nf_weather_planning_factor_today",
    "sensor.se_nf_weather_lead_minutes",
    "sensor.se_nf_load_forecast_summary",
    "sensor.se_nf_live_pv_forecast_now",
]

WATCH_FUNCTIONAL = [
    "input_select.se_nf_session_state",
    "input_select.se_nf_optimization_mode",
    "input_boolean.se_netzdienlich_enabled",
    "input_boolean.se_nf_weather_planning_enabled",
    "input_number.se_nf_weather_current_weight_pct",
    "input_number.se_nf_weather_max_lead_min",
    "input_number.se_nf_planning_charge_power_w",
    "input_number.se_nf_start_safety_buffer_min",
    "input_number.se_nf_lifetime_start_safety_buffer_min",
    "input_number.se_nf_lifetime_latest_finish_hour",
    "sensor.se_nf_config_check",
    "sensor.se_nf_sanity_check",
    "sensor.se_nf_needed_energy",
    "sensor.se_nf_required_charge_minutes",
    "sensor.se_nf_mode_start_safety_buffer_min",
    "sensor.se_nf_mode_min_start_hour",
    "sensor.se_nf_mode_latest_finish_hour",
    "sensor.se_nf_weather_current_factor",
    "sensor.se_nf_weather_planning_factor_today",
    "sensor.se_nf_weather_lead_minutes",
    "sensor.se_nf_available_pv_for_battery_today",
    "sensor.se_nf_coverage_ratio",
    "sensor.se_nf_live_battery_pv_margin",
    "sensor.se_nf_load_forecast_source",
    "sensor.se_nf_load_forecast_summary",
    "sensor.se_nf_load_coverage_lead_minutes",
    "sensor.se_nf_adaptive_forecast_bias_minutes",
    "sensor.se_nf_adaptive_forecast_summary",
    "sensor.se_nf_live_forecast_gap_lead_minutes",
    "sensor.se_nf_live_pv_forecast_now",
    "sensor.se_nf_live_pv_actual_now",
    "sensor.se_nf_today_planned_start_candidate_timestamp",
    "sensor.se_nf_active_planned_start_timestamp",
    "input_datetime.se_nf_session_planned_start",
    "sensor.se_nf_today_charge_window",
    "sensor.se_nf_tomorrow_charge_window",
    "sensor.se_nf_decision_reason",
    "sensor.se_nf_writer_mode",
    "sensor.se_nf_charge_limit_target",
    "sensor.se_nf_desired_target",
    "sensor.se_nf_charge_limit_actual",
    "number.solaredge_i1_storage_charge_limit",
    "number.solaredge_i1_storage_discharge_limit",
]

def api_get(path):
    req = urllib.request.Request(API + path, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode())

def api_post(path, data):
    req = urllib.request.Request(
        API + path,
        data=json.dumps(data).encode(),
        headers=HEADERS,
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        raw = r.read().decode()
        return json.loads(raw) if raw else None

def state(entity_id):
    try:
        return api_get("/states/" + entity_id).get("state")
    except Exception:
        return "missing"

def attrs(entity_id):
    try:
        return api_get("/states/" + entity_id).get("attributes", {})
    except Exception:
        return {}

def fnum(entity_id, default=None):
    v = state(entity_id)
    try:
        return float(v)
    except Exception:
        return default

def ts_hhmm(v):
    try:
        i = int(float(v))
        if i <= 0:
            return "0"
        return datetime.fromtimestamp(i).strftime("%H:%M")
    except Exception:
        return str(v)

def write_report(name, lines):
    p = RUN_DIR / name
    p.write_text("\n".join(str(x) for x in lines) + "\n")
    print(f"Report: {p}")
    return p

def read_files():
    files = sorted(PACKAGE_DIR.glob("*.yaml"))
    data = {}
    for p in files:
        try:
            data[p] = p.read_text(errors="ignore")
        except Exception as e:
            data[p] = f"<<READ ERROR {e}>>"
    return data

def extract_refs(text):
    refs = set()

    patterns = [
        r"states\(\s*['\"]([^'\"]+)['\"]\s*\)",
        r"is_state\(\s*['\"]([^'\"]+)['\"]\s*,",
        r"state_attr\(\s*['\"]([^'\"]+)['\"]\s*,",
        r"expand\(\s*['\"]([^'\"]+)['\"]\s*\)",
        r"has_value\(\s*['\"]([^'\"]+)['\"]\s*\)",
    ]

    for pat in patterns:
        for m in re.finditer(pat, text):
            refs.add(m.group(1).strip())

    # entity_id: xyz und Listen grob erkennen
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("entity_id:"):
            val = stripped.split("entity_id:", 1)[1].strip().strip("'\"")
            if val and "." in val and " " not in val:
                refs.add(val)
        elif stripped.startswith("- ") and "." in stripped and not stripped.startswith("- name:"):
            val = stripped[2:].strip().strip("'\"")
            if re.match(r"^[a-zA-Z0-9_]+\.[a-zA-Z0-9_]+$", val):
                refs.add(val)

    return refs

def exact_refs_in_file(entity_id, text):
    out = []
    for i, line in enumerate(text.splitlines(), start=1):
        if entity_id in line:
            out.append((i, line.strip()))
    return out

def classify_external(eid):
    if eid in [
        "input_boolean.se_netzdienlich_enabled",
        "input_boolean.se_netzdienlich_debug",
        "sensor.speicher_ziel_ladestand",
    ]:
        return "core"
    if eid.startswith(CORE_PREFIXES):
        return "core"
    if eid.startswith(HELPER_PREFIXES):
        return "helper_external_or_missing_definition"
    if eid.startswith(SOLAREDGE_PREFIXES):
        return "required_solaredge"
    if eid.startswith(OPTIONAL_PREFIXES):
        return "optional_external"
    if eid.startswith(("weather.", "sun.", "sensor.power_", "binary_sensor.power_")):
        return "local_hardcoded_or_needs_mapping"
    if eid.startswith(("sensor.pv_", "sensor.power_", "sensor.energy_")):
        return "local_hardcoded_or_needs_mapping"
    return "external_unknown"

def get_all_states_map():
    states = api_get("/states")
    return {s.get("entity_id"): s for s in states}

def run_ha_core_check():
    lines = []
    lines.append("=== HA CORE CHECK ===")
    try:
        proc = subprocess.run(
            ["ha", "core", "check"],
            capture_output=True,
            text=True,
            timeout=180,
        )
        lines.append("returncode: " + str(proc.returncode))
        lines.append("--- stdout ---")
        lines.append(proc.stdout.strip())
        lines.append("--- stderr ---")
        lines.append(proc.stderr.strip())
    except Exception as e:
        lines.append("ERROR: " + repr(e))
    return lines

def audit_static():
    lines = []
    files = read_files()
    states_map = get_all_states_map()

    lines.append("=== SE NF RELEASE STATIC PACKAGE AUDIT ===")
    lines.append("Zeit: " + datetime.now().isoformat())
    lines.append("Run dir: " + str(RUN_DIR))
    lines.append("Package dir: " + str(PACKAGE_DIR))
    lines.append("Main package exists: " + str(MAIN.exists()))
    lines.append("YAML package count: " + str(len(files)))
    lines.append("")

    # 1. HA core check
    lines.extend(run_ha_core_check())
    lines.append("")

    # 2. Package-Dateien
    lines.append("=== PACKAGE FILES ===")
    for p in files:
        lines.append(f"{p} | {len(files[p].splitlines())} lines")
    lines.append("")

    # 3. Unique IDs Duplikate
    lines.append("=== UNIQUE_ID DUPLICATES ===")
    unique = {}
    for p, text in files.items():
        for i, line in enumerate(text.splitlines(), start=1):
            m = re.search(r"unique_id:\s*['\"]?([^'\"\s#]+)", line)
            if m:
                unique.setdefault(m.group(1), []).append((p, i))
    dup = {k: v for k, v in unique.items() if len(v) > 1}
    if not dup:
        lines.append("PASS: keine duplicate unique_id gefunden")
    else:
        for k, v in sorted(dup.items()):
            lines.append(f"FAIL: duplicate unique_id {k}")
            for p, i in v:
                lines.append(f"  {p}:{i}")
    lines.append("")

    # 4. Alte Legacy-Referenzen im Hauptpaket
    lines.append("=== LEGACY REFERENCES IN MAIN ===")
    main_text = files.get(MAIN, "")
    legacy_hits = []
    for eid in KNOWN_LEGACY_MUST_NOT_BE_IN_MAIN:
        refs = exact_refs_in_file(eid, main_text)
        for line, txt in refs:
            legacy_hits.append((eid, line, txt))
    if not legacy_hits:
        lines.append("PASS: keine bekannten Legacy-Referenzen im Hauptpaket")
    else:
        for eid, line, txt in legacy_hits:
            lines.append(f"FAIL: {eid} in main:{line}: {txt}")
    lines.append("")

    # 5. Entity-Refs und Portabilität
    lines.append("=== ENTITY REFERENCE PORTABILITY ===")
    all_refs = {}
    for p, text in files.items():
        for eid in extract_refs(text):
            all_refs.setdefault(eid, set()).add(p)

    categories = {}
    for eid, ps in all_refs.items():
        categories.setdefault(classify_external(eid), []).append((eid, ps))

    for cat in [
        "core",
        "required_solaredge",
        "optional_external",
        "local_hardcoded_or_needs_mapping",
        "helper_external_or_missing_definition",
        "external_unknown",
    ]:
        rows = sorted(categories.get(cat, []))
        lines.append("")
        lines.append(f"--- {cat} ({len(rows)}) ---")
        for eid, ps in rows:
            st = states_map.get(eid, {}).get("state", "missing")
            mark = ""
            if str(st) in BAD:
                mark = " <<< BAD_NOW"
            lines.append(f"{eid:65} | state={st:16} | files={len(ps)}{mark}")

    # 6. Missing referenced entities
    lines.append("")
    lines.append("=== MISSING OR BAD REFERENCED ENTITIES ===")
    missing_or_bad = []
    for eid, ps in sorted(all_refs.items()):
        st = states_map.get(eid, {}).get("state", "missing")
        if st == "missing" or str(st) in BAD:
            crit = any(k in eid.lower() for k in CRITICAL_KEYWORDS)
            in_main = MAIN in ps
            missing_or_bad.append((crit, in_main, eid, st, ps))

    for crit, in_main, eid, st, ps in sorted(missing_or_bad, key=lambda x: (not x[0], not x[1], x[2])):
        sev = "ROT" if crit and in_main else "ORANGE" if in_main else "GELB"
        lines.append(f"{sev}: {eid} = {st} | files: " + ", ".join(str(p.name) for p in sorted(ps)))
    if not missing_or_bad:
        lines.append("PASS: keine missing/bad referenzierten Entities")
    lines.append("")

    # 7. Hauptpaket critical summary exact
    critical_main = []
    referenced_main = []
    for eid, ps in all_refs.items():
        if MAIN not in ps:
            continue
        st = states_map.get(eid, {}).get("state", "missing")
        if st == "missing" or str(st) in BAD:
            if any(k in eid.lower() for k in CRITICAL_KEYWORDS):
                critical_main.append((eid, st))
            else:
                referenced_main.append((eid, st))

    lines.append("=== RELEASE GATE: MAIN BAD DEPENDENCIES ===")
    lines.append(f"critical_main: {len(critical_main)}")
    for eid, st in sorted(critical_main):
        lines.append(f"  ROT: {eid} = {st}")
    lines.append(f"referenced_main_noncritical: {len(referenced_main)}")
    for eid, st in sorted(referenced_main):
        lines.append(f"  ORANGE: {eid} = {st}")

    if len(critical_main) == 0:
        lines.append("GATE_STATIC_MAIN_CRITICAL: PASS")
    else:
        lines.append("GATE_STATIC_MAIN_CRITICAL: FAIL")

    return write_report("01_static_package_portability_audit.txt", lines)

def audit_runtime():
    lines = []
    lines.append("=== SE NF RUNTIME PLAUSIBILITY AUDIT ===")
    lines.append("Zeit: " + datetime.now().isoformat())
    lines.append("")

    # Snapshot
    lines.append("=== FUNCTIONAL SNAPSHOT ===")
    for e in WATCH_FUNCTIONAL:
        st = state(e)
        a = attrs(e)
        unit = a.get("unit_of_measurement", "")
        if "timestamp" in e:
            lines.append(f"{e:65} | {st:22} | {ts_hhmm(st):5} | {unit}")
        else:
            lines.append(f"{e:65} | {str(st):22} | {unit}")
    lines.append("")

    checks = []

    def check(name, ok, detail):
        checks.append((name, bool(ok), detail))

    # Basis
    check("config_check_ok", state("sensor.se_nf_config_check") == "ok", state("sensor.se_nf_config_check"))
    check("sanity_check_ok", state("sensor.se_nf_sanity_check") == "ok", state("sensor.se_nf_sanity_check"))

    target = fnum("sensor.se_nf_charge_limit_target", None)
    desired = fnum("sensor.se_nf_desired_target", None)
    actual = fnum("sensor.se_nf_charge_limit_actual", None)
    check("writer_target_numeric", target is not None and desired is not None and actual is not None, f"target={target}, desired={desired}, actual={actual}")

    mode = state("sensor.se_nf_writer_mode")
    check("writer_mode_valid", mode in ["idle", "open", "close", "blocked_cooldown", "blocked_lock", "blocked_config", "unknown", "missing"] or isinstance(mode, str), mode)

    # Wetter
    weather_enabled = state("input_boolean.se_nf_weather_planning_enabled")
    final = fnum("sensor.se_nf_weather_planning_factor_today", None)
    weather_lead = fnum("sensor.se_nf_weather_lead_minutes", None)
    check("weather_factor_range", final is not None and 0.2 <= final <= 1.2, f"final={final}")
    check("weather_lead_range", weather_lead is not None and 0 <= weather_lead <= 240, f"lead={weather_lead}")

    # PV und Bedarf
    need = fnum("sensor.se_nf_needed_energy", None)
    avail = fnum("sensor.se_nf_available_pv_for_battery_today", None)
    coverage = fnum("sensor.se_nf_coverage_ratio", None)
    check("needed_energy_valid", need is not None and need >= 0, f"need={need}")
    check("available_pv_valid", avail is not None and avail >= -1, f"available={avail}")
    if need is not None and avail is not None and coverage is not None and need > 0.05:
        calc_cov = round(avail / need, 2)
        check("coverage_ratio_plausible", abs(calc_cov - coverage) <= 0.25, f"coverage={coverage}, calc={calc_cov}, avail={avail}, need={need}")
    else:
        check("coverage_ratio_plausible", True, f"nicht prüfbar: coverage={coverage}, avail={avail}, need={need}")

    # Ladezeit
    req = fnum("sensor.se_nf_required_charge_minutes", None)
    power = fnum("input_number.se_nf_planning_charge_power_w", None)
    if need is not None and power and power > 0:
        expected_req = int(-(-need * 60 * 1000 // power))  # ceil
        check("required_charge_minutes_plausible", req is not None and abs(req - expected_req) <= 3, f"req={req}, expected={expected_req}, need={need}, power={power}")
    else:
        check("required_charge_minutes_plausible", True, f"nicht prüfbar: req={req}, need={need}, power={power}")

    # Candidate Timestamp grob plausibel
    cand = fnum("sensor.se_nf_today_planned_start_candidate_timestamp", None)
    active = fnum("sensor.se_nf_active_planned_start_timestamp", None)
    planned_ts = attrs("input_datetime.se_nf_session_planned_start").get("timestamp")
    try:
        planned_ts = float(planned_ts)
    except Exception:
        planned_ts = None

    check("candidate_timestamp_valid", cand is not None and cand >= 0, f"candidate={cand} {ts_hhmm(cand)}")
    check("active_timestamp_valid", active is not None and active >= 0, f"active={active} {ts_hhmm(active)}")
    if cand and active:
        check("candidate_active_delta_reasonable", abs(cand - active) <= 7200, f"candidate={ts_hhmm(cand)}, active={ts_hhmm(active)}")
    if active and planned_ts:
        check("active_planned_delta_reasonable", abs(active - planned_ts) <= 7200, f"active={ts_hhmm(active)}, planned={ts_hhmm(planned_ts)}")

    # Forecast / SQL
    live_forecast = fnum("sensor.se_nf_live_pv_forecast_now", None)
    check("live_pv_forecast_now_valid", live_forecast is not None and live_forecast >= 0, f"forecast_now={live_forecast}")

    load_summary = state("sensor.se_nf_load_forecast_summary")
    check("load_forecast_summary_valid", load_summary not in BAD and load_summary != "missing", load_summary)

    # Window Texte
    today_window = state("sensor.se_nf_today_charge_window")
    decision = state("sensor.se_nf_decision_reason")
    check(
        "today_charge_window_valid",
        today_window not in BAD
        and today_window != "missing"
        and (
            "Bedarf" in today_window
            or "keine Ladung nötig" in today_window
            or "Akku voll" in today_window
            or "Tagesfenster beendet" in today_window
            or "Tagesfenster erledigt" in today_window
        ),
        today_window
    )
    check("decision_reason_valid", decision not in BAD and decision != "missing", decision)

    # Ergebnis
    lines.append("=== PLAUSIBILITY CHECKS ===")
    fail_count = 0
    warn_count = 0
    for name, ok, detail in checks:
        if ok:
            lines.append(f"PASS: {name} | {detail}")
        else:
            fail_count += 1
            lines.append(f"FAIL: {name} | {detail}")

    lines.append("")
    lines.append("=== RELEASE GATE: RUNTIME ===")
    lines.append(f"runtime_fail_count: {fail_count}")
    lines.append("GATE_RUNTIME: " + ("PASS" if fail_count == 0 else "FAIL"))

    return write_report("02_runtime_plausibility_audit.txt", lines)

def audit_existing_testers():
    lines = []
    lines.append("=== EXISTING TESTER BRIDGE ===")
    lines.append("Zeit: " + datetime.now().isoformat())
    lines.append("")

    files = sorted(PACKAGE_DIR.glob("*tester*.yaml")) + sorted(PACKAGE_DIR.glob("*health*.yaml"))
    seen = []
    lines.append("=== TESTER/HEALTH PACKAGES ===")
    for p in files:
        if p not in seen:
            seen.append(p)
            try:
                txt = p.read_text(errors="ignore")
                lines.append(f"{p} | {len(txt.splitlines())} lines")
            except Exception as e:
                lines.append(f"{p} | READ_ERROR {e}")

    lines.append("")
    lines.append("=== EXISTING TESTER STATE SENSORS ===")
    for e in [
        "sensor.se_nf_config_check",
        "sensor.se_nf_sanity_check",
        "sensor.se_nf_lifetime_latch_repair_status",
        "sensor.se_nf_writer_last_decision",
        "sensor.se_nf_decision_reason",
    ]:
        lines.append(f"{e}: {state(e)}")

    lines.append("")
    lines.append("=== SHARE TEST REPORT CANDIDATES ===")
    candidates = []
    roots = [
        Path("/share"),
        Path("/share/HomeAssist"),
        Path("/share/HomeAssist/system_health_tester"),
    ]
    for root in roots:
        if root.exists():
            for pat in ["*.txt", "*.json", "*.log"]:
                candidates.extend(root.glob(pat))
            for sub in root.glob("*tester*"):
                if sub.is_dir():
                    for pat in ["*.txt", "*.json", "*.log"]:
                        candidates.extend(sub.glob(pat))

    candidates = sorted(set(candidates), key=lambda p: p.stat().st_mtime if p.exists() else 0, reverse=True)[:30]
    for p in candidates:
        try:
            size = p.stat().st_size
            mtime = datetime.fromtimestamp(p.stat().st_mtime).isoformat()
            lines.append(f"{p} | {size} bytes | {mtime}")
            if size < 300000:
                txt = p.read_text(errors="ignore")
                interesting = []
                for line in txt.splitlines():
                    ll = line.lower()
                    if any(k in ll for k in ["fail", "error", "control_fault", "blocked", "critical", "unavailable", "unknown"]):
                        interesting.append(line[:220])
                for x in interesting[:8]:
                    lines.append("  hit: " + x)
        except Exception as e:
            lines.append(f"{p} | ERROR {e}")

    return write_report("03_existing_tester_bridge.txt", lines)

def audit_safe_ab():
    lines = []
    lines.append("=== SAFE FUNCTIONAL A/B TESTS ===")
    lines.append("Zeit: " + datetime.now().isoformat())
    lines.append("")

    session = state("input_select.se_nf_session_state")
    target = fnum("sensor.se_nf_charge_limit_target", 999)
    desired = fnum("sensor.se_nf_desired_target", 999)
    actual = fnum("sensor.se_nf_charge_limit_actual", 999)

    lines.append(f"session={session}")
    lines.append(f"target={target}")
    lines.append(f"desired={desired}")
    lines.append(f"actual={actual}")
    lines.append("")

    if session not in ["closed", "armed"] or target != 0 or desired != 0:
        lines.append("ABBRUCH: Anlage nicht im ruhigen Planungszustand.")
        lines.append("Safe-AB-Test läuft nur bei session closed/armed und target/desired 0.")
        return write_report("04_safe_ab_tests_ABORTED.txt", lines)

    def set_number(e, v):
        api_post("/services/input_number/set_value", {"entity_id": e, "value": float(v)})

    def set_bool(e, v):
        svc = "turn_on" if v == "on" else "turn_off"
        api_post(f"/services/input_boolean/{svc}", {"entity_id": e})

    def set_datetime(e, v):
        api_post("/services/input_datetime/set_datetime", {"entity_id": e, "datetime": v})

    watch = [
        "sensor.se_nf_weather_planning_factor_today",
        "sensor.se_nf_weather_lead_minutes",
        "sensor.se_nf_required_charge_minutes",
        "sensor.se_nf_available_pv_for_battery_today",
        "sensor.se_nf_coverage_ratio",
        "sensor.se_nf_load_coverage_lead_minutes",
        "sensor.se_nf_adaptive_forecast_bias_minutes",
        "sensor.se_nf_live_forecast_gap_lead_minutes",
        "sensor.se_nf_today_planned_start_candidate_timestamp",
        "sensor.se_nf_active_planned_start_timestamp",
        "input_datetime.se_nf_session_planned_start",
        "sensor.se_nf_today_charge_window",
        "sensor.se_nf_decision_reason",
    ]

    def snap(label):
        time.sleep(12)
        d = {}
        lines.append("")
        lines.append("=" * 80)
        lines.append(label)
        lines.append("=" * 80)
        for e in watch:
            v = state(e)
            d[e] = v
            if "timestamp" in e:
                lines.append(f"{e}: {v} ({ts_hhmm(v)})")
            else:
                lines.append(f"{e}: {v}")
        return d

    def diff(a, b):
        out = []
        for e in watch:
            if a.get(e) != b.get(e):
                out.append((e, a.get(e), b.get(e)))
        return out

    old = {
        "weather": state("input_boolean.se_nf_weather_planning_enabled"),
        "weather_weight": state("input_number.se_nf_weather_current_weight_pct"),
        "lifetime_buffer": state("input_number.se_nf_lifetime_start_safety_buffer_min"),
        "normal_buffer": state("input_number.se_nf_start_safety_buffer_min"),
        "planning_power": state("input_number.se_nf_planning_charge_power_w"),
        "planned": state("input_datetime.se_nf_session_planned_start"),
    }

    lines.append("Restore-Werte:")
    for k, v in old.items():
        lines.append(f"{k}: {v}")

    try:
        base = snap("BASELINE")

        # Wetter EIN/AUS + Gewicht
        set_bool("input_boolean.se_nf_weather_planning_enabled", "off")
        w_off = snap("WETTER AUS")

        set_bool("input_boolean.se_nf_weather_planning_enabled", "on")
        set_number("input_number.se_nf_weather_current_weight_pct", 0)
        w_0 = snap("WETTER EIN · GEWICHT 0")

        set_number("input_number.se_nf_weather_current_weight_pct", 80)
        w_80 = snap("WETTER EIN · GEWICHT 80")

        lines.append("")
        lines.append("=== WEATHER DIFF SUMMARY ===")
        for name, a, b in [
            ("off -> weight0", w_off, w_0),
            ("weight0 -> weight80", w_0, w_80),
        ]:
            lines.append(f"-- {name} --")
            changes = diff(a, b)
            if not changes:
                lines.append("keine Änderung sichtbar")
            for e, va, vb in changes:
                lines.append(f"{e}: {va} -> {vb}")

        # Modus-Startpuffer aktiv prüfen
        mode = state("input_select.se_nf_optimization_mode")
        if mode == "Akku schonen":
            buf_entity = "input_number.se_nf_lifetime_start_safety_buffer_min"
            high = 120
        else:
            buf_entity = "input_number.se_nf_start_safety_buffer_min"
            high = 180

        set_number(buf_entity, 0)
        b0 = snap(f"STARTPUFFER TEST · {buf_entity} = 0")

        set_number(buf_entity, high)
        bh = snap(f"STARTPUFFER TEST · {buf_entity} = {high}")

        lines.append("")
        lines.append("=== BUFFER DIFF SUMMARY ===")
        changes = diff(b0, bh)
        if not changes:
            lines.append("FAIL_OR_CONTEXT: Startpuffer zeigte keine sichtbare Wirkung im aktuellen Zustand.")
        else:
            for e, va, vb in changes:
                lines.append(f"{e}: {va} -> {vb}")

        # Planungsleistung
        set_number("input_number.se_nf_planning_charge_power_w", 2500)
        p_low = snap("PLANUNGSLEISTUNG 2500 W")

        set_number("input_number.se_nf_planning_charge_power_w", 5000)
        p_high = snap("PLANUNGSLEISTUNG 5000 W")

        lines.append("")
        lines.append("=== PLANNING POWER DIFF SUMMARY ===")
        changes = diff(p_low, p_high)
        if not changes:
            lines.append("FAIL_OR_CONTEXT: Planungsleistung zeigte keine sichtbare Wirkung.")
        else:
            for e, va, vb in changes:
                lines.append(f"{e}: {va} -> {vb}")

    finally:
        lines.append("")
        lines.append("=" * 80)
        lines.append("RESTORE")
        lines.append("=" * 80)

        try:
            set_bool("input_boolean.se_nf_weather_planning_enabled", old["weather"])
            set_number("input_number.se_nf_weather_current_weight_pct", old["weather_weight"])
            set_number("input_number.se_nf_lifetime_start_safety_buffer_min", old["lifetime_buffer"])
            set_number("input_number.se_nf_start_safety_buffer_min", old["normal_buffer"])
            set_number("input_number.se_nf_planning_charge_power_w", old["planning_power"])
            time.sleep(5)
            if old["planned"] not in BAD and old["planned"] != "missing":
                set_datetime("input_datetime.se_nf_session_planned_start", old["planned"])
            time.sleep(8)
        except Exception as e:
            lines.append("RESTORE_ERROR: " + repr(e))

        for k, ent in [
            ("weather", "input_boolean.se_nf_weather_planning_enabled"),
            ("weather_weight", "input_number.se_nf_weather_current_weight_pct"),
            ("lifetime_buffer", "input_number.se_nf_lifetime_start_safety_buffer_min"),
            ("normal_buffer", "input_number.se_nf_start_safety_buffer_min"),
            ("planning_power", "input_number.se_nf_planning_charge_power_w"),
            ("planned", "input_datetime.se_nf_session_planned_start"),
            ("target", "sensor.se_nf_charge_limit_target"),
            ("desired", "sensor.se_nf_desired_target"),
            ("actual", "sensor.se_nf_charge_limit_actual"),
        ]:
            lines.append(f"{k}: {state(ent)}")

    return write_report("04_safe_functional_ab_tests.txt", lines)

def release_summary():
    lines = []
    lines.append("=== SE NF RELEASE AUDIT SUMMARY ===")
    lines.append("Zeit: " + datetime.now().isoformat())
    lines.append("Run dir: " + str(RUN_DIR))
    lines.append("")

    for p in sorted(RUN_DIR.glob("*.txt")):
        txt = p.read_text(errors="ignore")
        lines.append(f"--- {p.name} ---")
        for key in [
            "GATE_STATIC_MAIN_CRITICAL",
            "GATE_RUNTIME",
            "critical_main:",
            "runtime_fail_count:",
            "ABBRUCH:",
            "RESTORE_ERROR:",
            "FAIL:",
            "FAIL_OR_CONTEXT:",
        ]:
            hits = [line for line in txt.splitlines() if key in line]
            for h in hits[:20]:
                lines.append(h)
        lines.append("")

    # Gate grob berechnen
    all_txt = "\n".join(p.read_text(errors="ignore") for p in sorted(RUN_DIR.glob("*.txt")))
    hard_fail = False
    if "GATE_STATIC_MAIN_CRITICAL: FAIL" in all_txt:
        hard_fail = True
    if "GATE_RUNTIME: FAIL" in all_txt:
        hard_fail = True
    if "RESTORE_ERROR:" in all_txt:
        hard_fail = True

    lines.append("=== RELEASE GATE OVERALL ===")
    lines.append("OVERALL: " + ("FAIL" if hard_fail else "PASS_OR_REVIEW"))
    lines.append("")
    lines.append("Hinweis:")
    lines.append("- PASS_OR_REVIEW bedeutet: keine harte Blockade gefunden; Safe-AB-Ergebnisse trotzdem fachlich lesen.")
    lines.append("- FAIL_OR_CONTEXT bei A/B kann kontextbedingt ok sein, wenn ein Grenzwert im aktuellen Zustand nicht wirksam werden kann.")

    return write_report("99_release_audit_summary.txt", lines)

def main():
    if not TOKEN:
        print("FEHLER: SUPERVISOR_TOKEN fehlt. Script im Home-Assistant-Terminal ausführen.")
        sys.exit(1)

    mode = sys.argv[1] if len(sys.argv) > 1 else "readonly"

    if mode == "readonly":
        audit_static()
        audit_runtime()
        audit_existing_testers()
        release_summary()
    elif mode == "safe-ab":
        audit_safe_ab()
        release_summary()
    elif mode == "all":
        audit_static()
        audit_runtime()
        audit_existing_testers()
        audit_safe_ab()
        release_summary()
    else:
        print("Usage: se_nf_release_audit.py [readonly|safe-ab|all]")
        sys.exit(2)

    print("")
    print("FERTIG.")
    print("Run dir:", RUN_DIR)

if __name__ == "__main__":
    main()
