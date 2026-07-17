#!/usr/bin/env python3
"""Read-only acceptance test for the SolarEdge resilience target model."""

from __future__ import annotations

import json
import math
import os
import re
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


BAD = {"unknown", "unavailable", "none", "None", ""}
CONFIG = Path("/config")
PACKAGES = CONFIG / "packages"


def core_api(path: str):
    token = os.environ.get("SUPERVISOR_TOKEN", "")
    if not token:
        raise RuntimeError("SUPERVISOR_TOKEN nicht verfügbar")
    request = urllib.request.Request(
        "http://supervisor/core/api" + path,
        headers={"Authorization": f"Bearer {token}"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def finite(value, default=0.0):
    try:
        result = float(value)
    except (TypeError, ValueError):
        return default
    return result if math.isfinite(result) else default


def truthy(value):
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def close(left, right, tolerance):
    return abs(finite(left) - finite(right)) <= tolerance


def decimal_hour_text(value):
    hour = int(value)
    minute = int(round((value - hour) * 60))
    if minute >= 60:
        hour += 1
        minute -= 60
    return f"{hour % 24:02d}:{minute:02d}"


def named_sensor_block(text, name):
    lines = text.splitlines()
    pattern = re.compile(
        r'^(?P<indent>\s*)-\s+name:\s+["\']'
        + re.escape(name)
        + r'["\']\s*$'
    )
    matches = []
    for index, line in enumerate(lines):
        match = pattern.match(line)
        if match:
            matches.append((index, len(match.group("indent"))))
    if len(matches) != 1:
        return ""
    start, base_indent = matches[0]
    end = len(lines)
    for index in range(start + 1, len(lines)):
        stripped = lines[index].strip()
        if not stripped:
            continue
        indentation = len(lines[index]) - len(lines[index].lstrip())
        if indentation < base_indent:
            end = index
            break
        if indentation == base_indent and re.match(r"-\s+name:", stripped):
            end = index
            break
    return "\n".join(lines[start:end])


def scenario(
    *,
    capacity,
    reserve,
    night,
    daytime,
    buffer_pct,
    safety,
    pv_tomorrow,
    pv_overmorrow=None,
    minimum,
    maximum,
):
    factor = 1 + buffer_pct / 100
    buffered_night = night * factor
    buffered_day = daytime * factor
    s1 = buffered_night
    s2 = s1 + buffered_day - pv_tomorrow
    s3 = s2 + buffered_night
    prefixes = [0.0, s1, s2, s3]
    horizon = "through_night_2"
    if pv_overmorrow is not None:
        s4 = s3 + buffered_day - pv_overmorrow
        prefixes.append(s4)
        horizon = "through_day_2"
    required = round(max(prefixes) + safety, 2)
    raw = reserve + required / capacity * 100 if capacity > 0 else maximum
    target = round(min(max(raw, minimum), maximum), 1)
    usable = capacity * max(maximum - reserve, 0) / 100
    uncovered = round(max(required - usable, 0), 2)
    return {
        "required": required,
        "target": target,
        "uncovered": uncovered,
        "risk": uncovered > 0.10,
        "horizon": horizon,
    }


def main():
    print("SE_NF_RESILIENCE_ACCEPTANCE_TEST_V2")
    print("read_only: true")
    print("generated_utc:", datetime.now(timezone.utc).isoformat())

    checks = {}

    print("\n[STATIC_CONFIGURATION]")
    yaml_files = sorted(PACKAGES.glob("*.yaml"))
    contents = {path: path.read_text(encoding="utf-8") for path in yaml_files}
    combined = "\n".join(contents.values())
    unique_ids = Counter(
        re.findall(
            r"^\s*unique_id:\s*[\"']?([^\"'\s#]+)",
            combined,
            flags=re.MULTILINE,
        )
    )
    expected_unique_ids = [
        "se_nf_night_consumption_7d_dynamic",
        "se_nf_daytime_consumption_7d_dynamic",
        "se_nf_historical_daytime_consumption_7d_dynamic",
        "se_nf_resilience_required_energy",
        "se_nf_resilience_target_pct",
    ]
    for unique_id in expected_unique_ids:
        count = unique_ids[unique_id]
        print(f"{unique_id}: definitions={count}")
        checks[f"unique_{unique_id}"] = count == 1

    script_results = {}
    for script_name in (
        "se_nf_night_forecast_7d.py",
        "se_nf_daytime_forecast_7d.py",
    ):
        path = CONFIG / script_name
        try:
            source = path.read_text(encoding="utf-8")
            compile(source, str(path), "exec")
            script_results[script_name] = "PASS"
        except Exception as exc:
            script_results[script_name] = f"FAIL:{type(exc).__name__}"
    for name, result in script_results.items():
        print(f"{name}: {result}")
        checks[f"compile_{name}"] = result == "PASS"

    main_path = PACKAGES / "solaredge_netzdienlich.yaml"
    main_text = main_path.read_text(encoding="utf-8")
    night_block = named_sensor_block(
        main_text, "SE NF Lifetime Night Energy Forecast"
    )
    effective_block = named_sensor_block(
        main_text, "SE NF Effective Target SoC Pct"
    )
    compatibility_block = named_sensor_block(
        main_text, "Speicher Ziel Ladestand"
    )
    checks["night_uses_dynamic_history"] = (
        "sensor.se_nf_night_consumption_7d_dynamic" in night_block
    )
    checks["effective_uses_resilience"] = (
        "sensor.se_nf_resilience_target_pct" in effective_block
    )
    checks["compatibility_is_alias"] = (
        "sensor.se_nf_effective_target_soc_pct" in compatibility_block
    )
    for key in (
        "night_uses_dynamic_history",
        "effective_uses_resilience",
        "compatibility_is_alias",
    ):
        print(f"{key}: {checks[key]}")

    states = {item["entity_id"]: item for item in core_api("/states")}

    def item(entity_id):
        return states.get(entity_id, {"state": "unknown", "attributes": {}})

    def state(entity_id):
        return item(entity_id).get("state", "unknown")

    def attr(entity_id, name, default=None):
        return item(entity_id).get("attributes", {}).get(name, default)

    night_entity = "sensor.se_nf_night_consumption_7d_dynamic"
    day_entity = "sensor.se_nf_daytime_consumption_7d_dynamic"
    historical_day_entity = (
        "sensor.se_nf_historical_daytime_consumption_7d_dynamic"
    )
    required_entity = "sensor.se_nf_resilience_required_energy"
    resilience_target_entity = "sensor.se_nf_resilience_target_pct"
    effective_target_entity = "sensor.se_nf_effective_target_soc_pct"
    compatibility_target_entity = "sensor.speicher_ziel_ladestand"

    dynamic_hour = finite(state("sensor.se_nf_dynamic_night_end_hour"), 8.0)
    expected_boundary = decimal_hour_text(dynamic_hour)
    night_start = str(attr(night_entity, "window_start", ""))
    night_end = str(attr(night_entity, "window_end", ""))
    day_start = str(attr(day_entity, "window_start", ""))
    day_end = str(attr(day_entity, "window_end", ""))
    night_valid = truthy(attr(night_entity, "valid", False))
    day_valid = truthy(attr(day_entity, "valid", False))
    night_count = int(finite(attr(night_entity, "valid_nights", 0)))
    day_count = int(finite(attr(day_entity, "valid_days", 0)))

    print("\n[HISTORY_WINDOWS]")
    print("dynamic_boundary:", expected_boundary)
    print(
        "night:",
        state(night_entity),
        f"{night_start}-{night_end}",
        "valid=", night_valid,
        "samples=", night_count,
    )
    print(
        "daytime:",
        state(day_entity),
        f"{day_start}-{day_end}",
        "valid=", day_valid,
        "samples=", day_count,
    )
    print(
        "effective_daytime:",
        state(historical_day_entity),
        "source=", attr(historical_day_entity, "source"),
    )
    checks["night_history_valid"] = night_valid and night_count >= 3
    checks["day_history_valid"] = day_valid and day_count >= 3
    checks["windows_connect"] = night_end == day_start
    checks["dynamic_boundary_applied"] = (
        night_end == expected_boundary and day_start == expected_boundary
    )
    checks["daytime_median_active"] = (
        attr(historical_day_entity, "source") == "median_7_day_windows"
        and close(state(historical_day_entity), state(day_entity), 0.01)
    )

    capacity = finite(state("sensor.se_nf_battery_capacity_kwh"))
    reserve = finite(state("sensor.se_nf_backup_reserve_pct"))
    night = finite(state("sensor.se_nf_lifetime_night_energy_forecast"))
    daytime = finite(state(historical_day_entity))
    buffer_pct = finite(state("input_number.se_nf_lifetime_soc_buffer_pct"))
    safety = finite(state("input_number.se_nf_lifetime_safety_kwh"))
    pv1 = finite(state("sensor.se_nf_pv_forecast_tomorrow_weather_adjusted"))
    source2 = state("sensor.se_nf_adaptive_pv_overmorrow_source")
    valid2 = (
        source2.startswith("sensor.")
        and state(source2) not in BAD
    )
    pv2 = (
        finite(attr(required_entity, "pv_overmorrow_effective_kwh", 0))
        if valid2
        else None
    )
    minimum = finite(state("input_number.se_nf_lifetime_min_soc_pct"), 45)
    maximum = finite(state("input_number.se_nf_lifetime_max_soc_pct"), 85)

    actual_scenario = scenario(
        capacity=capacity,
        reserve=reserve,
        night=night,
        daytime=daytime,
        buffer_pct=buffer_pct,
        safety=safety,
        pv_tomorrow=pv1,
        pv_overmorrow=pv2,
        minimum=minimum,
        maximum=maximum,
    )
    reported_required = finite(state(required_entity))
    reported_resilience_target = finite(state(resilience_target_entity))
    mode = state("sensor.se_nf_optimization_mode_effective")
    expected_effective_target = (
        actual_scenario["target"]
        if mode == "Akku schonen"
        else finite(state("input_number.se_nf_target_soc_pct"))
    )
    reported_effective_target = finite(state(effective_target_entity))
    reported_compatibility_target = finite(state(compatibility_target_entity))

    print("\n[INDEPENDENT_MATH]")
    print("capacity_kwh:", capacity)
    print("reserve_pct:", reserve, "source=", attr("sensor.se_nf_backup_reserve_pct", "source"))
    print("night_kwh:", night)
    print("daytime_kwh:", daytime)
    print("buffer_pct:", buffer_pct)
    print("safety_kwh:", safety)
    print("pv_tomorrow_kwh:", pv1)
    print("pv_overmorrow_source:", source2)
    print("expected_required_kwh:", actual_scenario["required"])
    print("reported_required_kwh:", reported_required)
    print("expected_resilience_target_pct:", actual_scenario["target"])
    print("reported_resilience_target_pct:", reported_resilience_target)
    print("effective_target_pct:", reported_effective_target)
    print("compatibility_target_pct:", reported_compatibility_target)
    checks["required_math_matches"] = close(
        reported_required, actual_scenario["required"], 0.02
    )
    checks["resilience_target_math_matches"] = close(
        reported_resilience_target, actual_scenario["target"], 0.11
    )
    checks["effective_target_matches_mode"] = close(
        reported_effective_target, expected_effective_target, 0.11
    )
    checks["targets_equal"] = close(
        reported_effective_target, reported_compatibility_target, 0.01
    )

    risk_state = state("binary_sensor.se_nf_resilience_capacity_risk")
    uncovered = finite(attr(resilience_target_entity, "uncovered_at_max_kwh", 0))
    checks["risk_flag_consistent"] = (
        (risk_state == "on") == (uncovered > 0.10)
    )

    soe = finite(state("sensor.se_nf_battery_soe"))
    reported_need = finite(state("sensor.se_nf_needed_energy"))
    effective_soe = max(soe, reserve)
    expected_need = round(
        capacity * max(reported_effective_target - effective_soe, 0) / 100,
        2,
    ) if capacity > 0 else 0.0
    session = state("input_select.se_nf_session_state")
    desired = finite(state("sensor.se_nf_desired_target"))
    latch = state("input_boolean.se_nf_lifetime_target_reached")

    print("\n[CONTROL_STATE]")
    print("mode:", mode)
    print("battery_soe_pct:", soe)
    print("expected_needed_kwh:", expected_need)
    print("reported_needed_kwh:", reported_need)
    print("session_state:", session)
    print("target_latched:", latch)
    print("desired_charge_limit_w:", desired)
    print("config_check:", state("sensor.se_nf_config_check"))
    print("sanity_check:", state("sensor.se_nf_sanity_check"))
    checks["needed_energy_matches"] = close(reported_need, expected_need, 0.02)
    checks["no_charge_when_no_need"] = not (
        reported_need <= 0.05 and desired > 0.1
    )
    checks["config_check_ok"] = state("sensor.se_nf_config_check") == "ok"
    checks["sanity_check_ok"] = state("sensor.se_nf_sanity_check") == "ok"
    checks["refresh_automation_on"] = (
        any(
            entity_id.startswith("automation.")
            and value.get("state") == "on"
            and value.get("attributes", {}).get("id")
            == "se_nf_dynamic_consumption_history_refresh"
            for entity_id, value in states.items()
        )
    )

    scenarios = {
        "actual": actual_scenario,
        "tomorrow_pv_5": scenario(
            capacity=capacity,
            reserve=reserve,
            night=night,
            daytime=daytime,
            buffer_pct=buffer_pct,
            safety=safety,
            pv_tomorrow=5,
            pv_overmorrow=None,
            minimum=minimum,
            maximum=maximum,
        ),
        "tomorrow_pv_0": scenario(
            capacity=capacity,
            reserve=reserve,
            night=night,
            daytime=daytime,
            buffer_pct=buffer_pct,
            safety=safety,
            pv_tomorrow=0,
            pv_overmorrow=None,
            minimum=minimum,
            maximum=maximum,
        ),
        "two_days_pv_0": scenario(
            capacity=capacity,
            reserve=reserve,
            night=night,
            daytime=daytime,
            buffer_pct=buffer_pct,
            safety=safety,
            pv_tomorrow=0,
            pv_overmorrow=0,
            minimum=minimum,
            maximum=maximum,
        ),
        "no_backup_system": scenario(
            capacity=capacity,
            reserve=0,
            night=night,
            daytime=daytime,
            buffer_pct=buffer_pct,
            safety=safety,
            pv_tomorrow=pv1,
            pv_overmorrow=pv2,
            minimum=minimum,
            maximum=maximum,
        ),
        "buffer_0_pct": scenario(
            capacity=capacity,
            reserve=reserve,
            night=night,
            daytime=daytime,
            buffer_pct=0,
            safety=safety,
            pv_tomorrow=pv1,
            pv_overmorrow=pv2,
            minimum=minimum,
            maximum=maximum,
        ),
        "buffer_100_pct": scenario(
            capacity=capacity,
            reserve=reserve,
            night=night,
            daytime=daytime,
            buffer_pct=100,
            safety=safety,
            pv_tomorrow=pv1,
            pv_overmorrow=pv2,
            minimum=minimum,
            maximum=maximum,
        ),
    }
    print("\n[READ_ONLY_SCENARIO_MATRIX]")
    for name, result in scenarios.items():
        print(
            f"{name}: target={result['target']:.1f}%, "
            f"required={result['required']:.2f}kWh, "
            f"uncovered={result['uncovered']:.2f}kWh, "
            f"risk={'high' if result['risk'] else 'covered'}, "
            f"horizon={result['horizon']}"
        )
    checks["less_pv_never_reduces_target"] = (
        scenarios["tomorrow_pv_0"]["target"]
        >= scenarios["tomorrow_pv_5"]["target"]
        >= scenarios["actual"]["target"]
    )
    checks["more_buffer_never_reduces_target"] = (
        scenarios["buffer_100_pct"]["target"]
        >= scenarios["actual"]["target"]
        >= scenarios["buffer_0_pct"]["target"]
    )
    checks["no_backup_path_bounded"] = (
        minimum <= scenarios["no_backup_system"]["target"] <= maximum
    )
    checks["all_scenarios_bounded"] = all(
        minimum <= result["target"] <= maximum
        for result in scenarios.values()
    )

    print("\n[CHECKS]")
    for name in sorted(checks):
        print(f"{name}: {'PASS' if checks[name] else 'FAIL'}")
    failed = [name for name, passed in checks.items() if not passed]
    print("\n[RESULT]")
    print("checks_total:", len(checks))
    print("checks_passed:", len(checks) - len(failed))
    print("checks_failed:", len(failed))
    print("failed_checks:", failed)
    print("overall:", "PASS" if not failed else "FAIL")


if __name__ == "__main__":
    main()
