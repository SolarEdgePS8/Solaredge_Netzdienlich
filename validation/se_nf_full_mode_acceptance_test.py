#!/usr/bin/env python3
"""SolarEdge Netzdienlich full mode acceptance tester.

The default run is read-only.  With --execute the tester temporarily isolates
all known inverter writers, sweeps every configured optimization mode, checks
the target/energy/timing equations, exercises the session manager, and restores
the original Home Assistant state in a finally block.

No API token, host name, entity mapping or personal data is written to reports.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
import traceback
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable
from zoneinfo import ZoneInfo


VERSION = "SE_NF_FULL_MODE_ACCEPTANCE_TEST_V2"
BAD = {"", "unknown", "unavailable", "none", "null"}
RECOVERY_PATH = Path("/share/SE_NF_FULL_MODE_TEST_RECOVERY.json")

E = {
    "master": "input_boolean.se_netzdienlich_enabled",
    "mode": "input_select.se_nf_optimization_mode",
    "effective_mode": "sensor.se_nf_optimization_mode_effective",
    "session": "input_select.se_nf_session_state",
    "planned": "input_datetime.se_nf_session_planned_start",
    "lifetime_latch": "input_boolean.se_nf_lifetime_target_reached",
    "critical_latch": "input_boolean.se_nf_critical_deficit_latched_today",
    "config": "sensor.se_nf_config_check",
    "sanity": "sensor.se_nf_sanity_check",
    "risk": "binary_sensor.se_nf_risk_flag",
    "evcc": "binary_sensor.se_nf_evcc_grid_charge_request",
    "soe": "sensor.se_nf_battery_soe",
    "capacity": "sensor.se_nf_battery_capacity_kwh",
    "reserve": "sensor.se_nf_backup_reserve_pct",
    "normal_target": "input_number.se_nf_target_soc_pct",
    "resilience_target": "sensor.se_nf_resilience_target_pct",
    "effective_target": "sensor.se_nf_effective_target_soc_pct",
    "compat_target": "sensor.speicher_ziel_ladestand",
    "needed": "sensor.se_nf_needed_energy",
    "power": "input_number.se_nf_planning_charge_power_w",
    "required_min": "sensor.se_nf_required_charge_minutes",
    "net_min": "input_number.se_nf_min_start_hour",
    "net_end": "input_number.se_nf_latest_finish_hour",
    "net_buffer": "input_number.se_nf_start_safety_buffer_min",
    "life_min": "input_number.se_nf_lifetime_min_start_hour",
    "life_end": "input_number.se_nf_lifetime_latest_finish_hour",
    "life_buffer": "input_number.se_nf_lifetime_start_safety_buffer_min",
    "mode_min": "sensor.se_nf_mode_min_start_hour",
    "mode_end": "sensor.se_nf_mode_latest_finish_hour",
    "mode_buffer": "sensor.se_nf_mode_start_safety_buffer_min",
    "weather": "sensor.se_nf_weather_lead_minutes",
    "weather_tomorrow": "sensor.se_nf_weather_lead_minutes_tomorrow",
    "load": "sensor.se_nf_load_coverage_lead_minutes",
    "adaptive": "sensor.se_nf_adaptive_forecast_bias_minutes",
    "live_gap": "sensor.se_nf_live_forecast_gap_lead_minutes",
    "candidate": "sensor.se_nf_today_planned_start_candidate_timestamp",
    "tomorrow_candidate": "sensor.se_nf_tomorrow_planned_start_timestamp",
    "active": "sensor.se_nf_active_planned_start_timestamp",
    "end": "sensor.se_nf_today_end_timestamp",
    "window": "sensor.se_nf_today_charge_window",
    "desired": "sensor.se_nf_desired_target",
    "actual_limit": "sensor.se_nf_charge_limit_actual",
    "low_floor": "input_number.se_nf_low_soc_floor_pct",
    "end_grace": "sensor.se_nf_today_end_with_grace_timestamp",
}

AUTOMATION_IDS = {
    "plan_freeze": "se_nf_v28_plan_freeze",
    "session_manager": "se_nf_v28_session_manager",
    "single_writer": "se_nf_v28_single_writer",
    "writer_close_bypass": "se_nf_v294b_writer_close_bypass",
    "master_off_defaults": "se_nf_v294a_master_off_defaults",
    "latch_reset": "se_nf_v29_lifetime_latch_reset",
    "target_latch": "se_nf_v29_lifetime_target_latch",
    "latch_repair": "se_nf_v293c_lifetime_latch_repair",
    "critical_latch": "se_nf_v293g_critical_deficit_daily_latch",
    "critical_reset": "se_nf_v293g_critical_deficit_daily_latch_reset",
}


class HAError(RuntimeError):
    pass


class HAClient:
    def __init__(self) -> None:
        token = os.environ.get("SUPERVISOR_TOKEN") or os.environ.get("HASS_TOKEN")
        if not token:
            raise HAError("SUPERVISOR_TOKEN/HASS_TOKEN fehlt. Im Home-Assistant-Terminal ausführen.")
        self.base = os.environ.get("HASS_URL", "http://supervisor/core/api").rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    def request(self, method: str, path: str, payload: Any = None) -> Any:
        data = None if payload is None else json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            self.base + path,
            data=data,
            method=method,
            headers=self.headers,
        )
        try:
            with urllib.request.urlopen(req, timeout=20) as response:
                raw = response.read()
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")[:500]
            raise HAError(f"HA API {method} {path}: HTTP {exc.code}: {detail}") from exc
        except OSError as exc:
            raise HAError(f"HA API nicht erreichbar: {exc}") from exc
        return json.loads(raw) if raw else None

    def states(self) -> dict[str, dict[str, Any]]:
        return {item["entity_id"]: item for item in self.request("GET", "/states")}

    def config(self) -> dict[str, Any]:
        return self.request("GET", "/config")

    def service(self, domain: str, service: str, data: dict[str, Any]) -> Any:
        return self.request("POST", f"/services/{domain}/{service}", data)


class View:
    def __init__(self, states: dict[str, dict[str, Any]]) -> None:
        self.states = states

    def exists(self, entity_id: str) -> bool:
        return entity_id in self.states

    def raw(self, entity_id: str, default: str = "unknown") -> str:
        return str(self.states.get(entity_id, {}).get("state", default))

    def attr(self, entity_id: str, name: str, default: Any = None) -> Any:
        return self.states.get(entity_id, {}).get("attributes", {}).get(name, default)

    def num(self, entity_id: str, default: float | None = None) -> float | None:
        raw = self.raw(entity_id).strip()
        if raw.lower() in BAD:
            return default
        try:
            value = float(raw)
        except (TypeError, ValueError):
            return default
        return value if math.isfinite(value) else default


@dataclass
class Check:
    name: str
    status: str
    detail: str
    phase: str


@dataclass
class Report:
    checks: list[Check] = field(default_factory=list)
    modes: list[dict[str, Any]] = field(default_factory=list)
    session_modes: list[dict[str, Any]] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    cleanup_ok: bool = False

    def add(self, phase: str, name: str, ok: bool | None, detail: str) -> None:
        status = "SKIP" if ok is None else ("PASS" if ok else "FAIL")
        self.checks.append(Check(name=name, status=status, detail=detail, phase=phase))

    def warn(self, phase: str, name: str, detail: str) -> None:
        self.checks.append(Check(name=name, status="WARN", detail=detail, phase=phase))

    @property
    def failures(self) -> list[Check]:
        return [c for c in self.checks if c.status == "FAIL"]


def close(a: float | None, b: float | None, tolerance: float = 0.11) -> bool:
    return a is not None and b is not None and abs(a - b) <= tolerance


def integer(view: View, entity_id: str, default: int = 0) -> int:
    value = view.num(entity_id)
    return default if value is None else int(value)


def hour_timestamp(day: datetime, decimal_hour: float) -> int:
    hour = int(decimal_hour)
    minute = int(round((decimal_hour - hour) * 60))
    if minute >= 60:
        hour += 1
        minute -= 60
    local = day.replace(hour=hour, minute=minute, second=0, microsecond=0)
    return int(local.timestamp())


def parse_datetime_state(raw: str, tz: ZoneInfo) -> int:
    if raw.strip().lower() in BAD:
        return 0
    try:
        value = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        if value.tzinfo is None:
            value = value.replace(tzinfo=tz)
        return int(value.timestamp())
    except ValueError:
        return 0


def local_time(ts: int, tz: ZoneInfo) -> str:
    if ts <= 0:
        return "0"
    return datetime.fromtimestamp(ts, tz).isoformat(timespec="seconds")


def mode_expected_inputs(view: View, mode: str) -> tuple[float | None, float | None, float | None]:
    if mode == "Akku schonen":
        return view.num(E["life_min"]), view.num(E["life_end"]), view.num(E["life_buffer"])
    return view.num(E["net_min"]), view.num(E["net_end"]), view.num(E["net_buffer"])


def expected_math(view: View, mode: str, tz: ZoneInfo) -> dict[str, Any]:
    now = datetime.now(tz)
    min_hour, end_hour, safety_buffer = mode_expected_inputs(view, mode)
    if min_hour is None or end_hour is None or safety_buffer is None:
        raise ValueError("Modus-Zeitparameter fehlen")

    cap = view.num(E["capacity"])
    soe = view.num(E["soe"])
    reserve = view.num(E["reserve"], 0.0)
    normal_target = view.num(E["normal_target"])
    resilience = view.num(E["resilience_target"])
    effective = view.num(E["effective_target"])
    compatibility = view.num(E["compat_target"])

    if mode == "Akku schonen" and resilience is not None:
        canonical_target = resilience
        canonical_source = "resilience_target"
    elif mode == "Akku schonen":
        canonical_target = effective
        canonical_source = "effective_target_legacy"
    else:
        canonical_target = normal_target
        canonical_source = "configured_normal_target"

    planning_target = compatibility if compatibility is not None else effective
    if None in (cap, soe, planning_target):
        expected_need = None
    elif cap <= 0:
        expected_need = 0.0
    else:
        effective_soe = max(float(soe), float(reserve or 0.0))
        expected_need = round(cap * max(planning_target - effective_soe, 0.0) / 100.0, 2)

    power = view.num(E["power"])
    if expected_need is None or power is None:
        expected_required = None
    elif expected_need <= 0.05 or power <= 0:
        expected_required = 0
    else:
        expected_required = int(math.ceil((expected_need / (power / 1000.0)) * 60.0 - 1e-12))

    min_ts = hour_timestamp(now, min_hour)
    end_ts = hour_timestamp(now, end_hour)
    tomorrow = now + timedelta(days=1)
    tomorrow_min_ts = hour_timestamp(tomorrow, min_hour)
    tomorrow_end_ts = hour_timestamp(tomorrow, end_hour)

    weather = integer(view, E["weather"])
    weather_tomorrow = integer(view, E["weather_tomorrow"])
    load = integer(view, E["load"])
    adaptive = integer(view, E["adaptive"])
    live_gap = integer(view, E["live_gap"])

    if expected_need is None or expected_required is None:
        candidate = None
        tomorrow_candidate = None
    elif expected_need <= 0.05 or end_ts <= 0:
        candidate = 0
        tomorrow_candidate = 0
    else:
        lead = expected_required + int(safety_buffer) + weather + load + adaptive + live_gap
        candidate = max(end_ts - lead * 60, min_ts)
        tomorrow_lead = expected_required + int(safety_buffer) + weather_tomorrow
        tomorrow_candidate = max(tomorrow_end_ts - tomorrow_lead * 60, tomorrow_min_ts)

    return {
        "mode": mode,
        "capacity_kwh": cap,
        "soe_pct": soe,
        "reserve_pct": reserve,
        "normal_target_pct": normal_target,
        "resilience_target_pct": resilience,
        "effective_target_pct": effective,
        "compatibility_target_pct": compatibility,
        "canonical_target_pct": canonical_target,
        "canonical_target_source": canonical_source,
        "planning_target_pct": planning_target,
        "expected_needed_kwh": expected_need,
        "reported_needed_kwh": view.num(E["needed"]),
        "power_w": power,
        "expected_required_min": expected_required,
        "reported_required_min": view.num(E["required_min"]),
        "expected_min_hour": min_hour,
        "reported_min_hour": view.num(E["mode_min"]),
        "expected_end_hour": end_hour,
        "reported_end_hour": view.num(E["mode_end"]),
        "expected_buffer_min": safety_buffer,
        "reported_buffer_min": view.num(E["mode_buffer"]),
        "weather_lead_min": weather,
        "load_lead_min": load,
        "adaptive_lead_min": adaptive,
        "live_gap_lead_min": live_gap,
        "expected_min_timestamp": min_ts,
        "expected_end_timestamp": end_ts,
        "reported_end_timestamp": integer(view, E["end"]),
        "expected_candidate_timestamp": candidate,
        "reported_candidate_timestamp": integer(view, E["candidate"]),
        "expected_tomorrow_candidate_timestamp": tomorrow_candidate,
        "reported_tomorrow_candidate_timestamp": integer(view, E["tomorrow_candidate"]),
        "stored_timestamp": parse_datetime_state(view.raw(E["planned"]), tz),
        "active_timestamp": integer(view, E["active"]),
        "selected_source": view.attr(E["active"], "selected_source"),
        "window_valid": view.attr(E["window"], "window_valid"),
        "window_text": view.raw(E["window"]),
    }


def evaluate_mode(view: View, mode: str, tz: ZoneInfo) -> tuple[dict[str, Any], list[tuple[str, bool, str]]]:
    data = expected_math(view, mode, tz)
    checks: list[tuple[str, bool, str]] = []

    def add(name: str, ok: bool, detail: str) -> None:
        checks.append((name, ok, detail))

    selected = view.raw(E["mode"])
    effective_mode = view.raw(E["effective_mode"])
    add("selected_mode", selected == mode, f"selected={selected}, expected={mode}")
    add("effective_mode", effective_mode == mode, f"effective={effective_mode}, expected={mode}")
    add(
        "mode_min_start",
        close(data["reported_min_hour"], data["expected_min_hour"], 0.011),
        f"reported={data['reported_min_hour']}, expected={data['expected_min_hour']}",
    )
    add(
        "mode_latest_finish",
        close(data["reported_end_hour"], data["expected_end_hour"], 0.011),
        f"reported={data['reported_end_hour']}, expected={data['expected_end_hour']}",
    )
    add(
        "mode_safety_buffer",
        close(data["reported_buffer_min"], data["expected_buffer_min"], 0.1),
        f"reported={data['reported_buffer_min']}, expected={data['expected_buffer_min']}",
    )

    target = data["canonical_target_pct"]
    add(
        "effective_target_matches_canonical",
        close(data["effective_target_pct"], target),
        f"effective={data['effective_target_pct']}, canonical={target}, source={data['canonical_target_source']}",
    )
    add(
        "compatibility_target_is_alias",
        close(data["compatibility_target_pct"], data["effective_target_pct"]),
        f"compatibility={data['compatibility_target_pct']}, effective={data['effective_target_pct']}",
    )
    if mode == "Akku schonen" and data["resilience_target_pct"] is not None:
        add(
            "resilience_target_is_active",
            close(data["resilience_target_pct"], data["effective_target_pct"]),
            f"resilience={data['resilience_target_pct']}, effective={data['effective_target_pct']}",
        )

    add(
        "needed_energy_equation",
        close(data["reported_needed_kwh"], data["expected_needed_kwh"], 0.02),
        f"reported={data['reported_needed_kwh']}, expected={data['expected_needed_kwh']}",
    )
    add(
        "required_minutes_equation",
        close(data["reported_required_min"], data["expected_required_min"], 0.1),
        f"reported={data['reported_required_min']}, expected={data['expected_required_min']}",
    )
    add(
        "end_timestamp_equation",
        abs(data["reported_end_timestamp"] - data["expected_end_timestamp"]) <= 2,
        f"reported={data['reported_end_timestamp']}, expected={data['expected_end_timestamp']}",
    )
    add(
        "candidate_equation",
        data["expected_candidate_timestamp"] is not None
        and abs(data["reported_candidate_timestamp"] - data["expected_candidate_timestamp"]) <= 2,
        f"reported={data['reported_candidate_timestamp']}, expected={data['expected_candidate_timestamp']}",
    )
    add(
        "tomorrow_candidate_equation",
        data["expected_tomorrow_candidate_timestamp"] is not None
        and abs(
            data["reported_tomorrow_candidate_timestamp"]
            - data["expected_tomorrow_candidate_timestamp"]
        )
        <= 2,
        "reported="
        f"{data['reported_tomorrow_candidate_timestamp']}, "
        f"expected={data['expected_tomorrow_candidate_timestamp']}",
    )

    candidate = data["expected_candidate_timestamp"]
    if candidate and candidate > 0:
        add(
            "stored_start_replanned",
            abs(data["stored_timestamp"] - candidate) <= 2,
            f"stored={data['stored_timestamp']}, candidate={candidate}",
        )
        add(
            "active_start_matches_plan",
            abs(data["active_timestamp"] - candidate) <= 2,
            f"active={data['active_timestamp']}, candidate={candidate}, source={data['selected_source']}",
        )
        add(
            "start_before_end",
            data["active_timestamp"] < data["reported_end_timestamp"],
            f"active={data['active_timestamp']}, end={data['reported_end_timestamp']}",
        )
        add(
            "start_not_before_minimum",
            data["active_timestamp"] >= data["expected_min_timestamp"],
            f"active={data['active_timestamp']}, minimum={data['expected_min_timestamp']}",
        )
        add(
            "window_valid",
            data["window_valid"] is True,
            f"window_valid={data['window_valid']}, source={data['selected_source']}",
        )
    else:
        add(
            "no_need_candidate_zero",
            data["reported_candidate_timestamp"] == 0,
            f"needed={data['reported_needed_kwh']}, candidate={data['reported_candidate_timestamp']}",
        )
        add(
            "no_need_window_text",
            "keine ladung" in data["window_text"].lower(),
            f"window={data['window_text']}",
        )

    return data, checks


def automation_map(view: View) -> dict[str, str]:
    by_key: dict[str, str] = {}
    for entity_id, item in view.states.items():
        if not entity_id.startswith("automation."):
            continue
        attrs = item.get("attributes", {})
        automation_id = str(attrs.get("id", ""))
        friendly = str(attrs.get("friendly_name", "")).lower()
        for key, wanted in AUTOMATION_IDS.items():
            if automation_id == wanted:
                by_key[key] = entity_id
        if "plan freeze guard" in friendly:
            by_key.setdefault("plan_freeze", entity_id)
        elif "session manager" in friendly:
            by_key.setdefault("session_manager", entity_id)
        elif "single writer safety guard" in friendly:
            by_key.setdefault("single_writer", entity_id)
        elif "writer close bypass" in friendly:
            by_key.setdefault("writer_close_bypass", entity_id)
    return by_key


def wait_for(
    client: HAClient,
    predicate: Callable[[View], bool],
    timeout: float,
    interval: float = 1.0,
) -> View:
    deadline = time.monotonic() + timeout
    last = View(client.states())
    while time.monotonic() < deadline:
        last = View(client.states())
        if predicate(last):
            return last
        time.sleep(interval)
    return last


def service_entity(client: HAClient, domain: str, service: str, entity_id: str, **extra: Any) -> None:
    data: dict[str, Any] = {"entity_id": entity_id}
    data.update(extra)
    client.service(domain, service, data)


def select_option(client: HAClient, entity_id: str, option: str) -> None:
    service_entity(client, "input_select", "select_option", entity_id, option=option)


def set_boolean(client: HAClient, entity_id: str, state: str) -> None:
    service_entity(client, "input_boolean", "turn_on" if state == "on" else "turn_off", entity_id)


def set_automation(client: HAClient, entity_id: str, state: str) -> None:
    if state == "on":
        service_entity(client, "automation", "turn_on", entity_id)
    else:
        service_entity(client, "automation", "turn_off", entity_id, stop_actions=True)


def set_datetime(client: HAClient, entity_id: str, value: str) -> None:
    service_entity(client, "input_datetime", "set_datetime", entity_id, datetime=value.replace("T", " "))


def write_recovery_snapshot(
    original: View,
    auto: dict[str, str],
    original_automation: dict[str, str],
) -> Path:
    path = RECOVERY_PATH if RECOVERY_PATH.parent.is_dir() else Path("/tmp") / RECOVERY_PATH.name
    payload = {
        "version": VERSION,
        "created_utc": datetime.now(ZoneInfo("UTC")).isoformat(),
        "values": {
            "mode": original.raw(E["mode"]),
            "session": original.raw(E["session"]),
            "planned": original.raw(E["planned"]),
            "master": original.raw(E["master"]),
            "lifetime_latch": original.raw(E["lifetime_latch"]),
            "critical_latch": original.raw(E["critical_latch"]),
            "lifetime_latch_exists": original.exists(E["lifetime_latch"]),
            "critical_latch_exists": original.exists(E["critical_latch"]),
        },
        "automations": {
            key: {"entity_id": auto[key], "state": state}
            for key, state in original_automation.items()
        },
        "privacy": "no_token_no_host_no_entity_mappings",
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def recover_snapshot(client: HAClient, path: Path) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    values = payload["values"]
    automations = payload.get("automations", {})
    errors: list[str] = []

    def safe(label: str, fn: Callable[[], None]) -> None:
        try:
            fn()
        except Exception as exc:
            errors.append(f"{label}: {exc}")

    # Writers stay off while helpers are restored.  Their original state is
    # restored only in the final loop below.
    for key in ("single_writer", "writer_close_bypass", "master_off_defaults"):
        item = automations.get(key)
        if item:
            safe(f"isolate {key}", lambda i=item: set_automation(client, i["entity_id"], "off"))
    for key in ("session_manager", "plan_freeze"):
        item = automations.get(key)
        if item:
            safe(f"pause {key}", lambda i=item: set_automation(client, i["entity_id"], "off"))

    safe("restore mode", lambda: select_option(client, E["mode"], values["mode"]))
    safe("restore planned", lambda: set_datetime(client, E["planned"], values["planned"]))
    safe("restore session", lambda: select_option(client, E["session"], values["session"]))
    if values.get("lifetime_latch_exists"):
        safe(
            "restore lifetime latch",
            lambda: set_boolean(client, E["lifetime_latch"], values["lifetime_latch"]),
        )
    if values.get("critical_latch_exists"):
        safe(
            "restore critical latch",
            lambda: set_boolean(client, E["critical_latch"], values["critical_latch"]),
        )
    safe("restore master", lambda: set_boolean(client, E["master"], values["master"]))

    physical = {"single_writer", "writer_close_bypass", "master_off_defaults"}
    for key, item in automations.items():
        if key not in physical:
            safe(
                f"restore automation {key}",
                lambda i=item: set_automation(client, i["entity_id"], i["state"]),
            )
    for key in ("master_off_defaults", "writer_close_bypass", "single_writer"):
        item = automations.get(key)
        if item:
            safe(
                f"restore automation {key}",
                lambda i=item: set_automation(client, i["entity_id"], i["state"]),
            )
    if errors:
        raise HAError("Recovery unvollständig: " + "; ".join(errors))
    path.unlink(missing_ok=True)


def static_scan(report: Report) -> None:
    package_dir = Path("/config/packages")
    if not package_dir.is_dir():
        report.warn("STATIC", "package_directory", "/config/packages nicht gefunden")
        return
    text = "\n".join(
        path.read_text(encoding="utf-8", errors="replace")
        for path in package_dir.rglob("*.yaml")
        if path.is_file()
    )
    for unique_id in (
        "se_nf_today_planned_start_candidate_timestamp",
        "se_nf_active_planned_start_timestamp",
        "se_nf_effective_target_soc_pct",
        "speicher_ziel_ladestand",
        "se_nf_needed_energy",
    ):
        count = text.count(f"unique_id: {unique_id}")
        report.add("STATIC", f"unique_{unique_id}", count == 1, f"definitions={count}")


def preflight(client: HAClient, report: Report, execute: bool) -> tuple[View, ZoneInfo, dict[str, str]]:
    view = View(client.states())
    tz_name = str(client.config().get("time_zone", "UTC"))
    try:
        tz = ZoneInfo(tz_name)
    except Exception:
        tz = ZoneInfo("UTC")
        report.warn("PREFLIGHT", "timezone", f"{tz_name!r} ungültig; UTC wird verwendet")

    required = [
        E["master"], E["mode"], E["effective_mode"], E["session"], E["planned"],
        E["config"], E["sanity"], E["risk"], E["evcc"], E["critical_latch"],
        E["soe"], E["capacity"], E["reserve"], E["desired"],
        E["normal_target"], E["effective_target"], E["compat_target"], E["needed"],
        E["power"], E["required_min"], E["mode_min"], E["mode_end"], E["mode_buffer"],
        E["candidate"], E["tomorrow_candidate"], E["active"], E["end"], E["window"],
    ]
    missing = [entity for entity in required if not view.exists(entity)]
    report.add("PREFLIGHT", "required_entities", not missing, f"missing={missing}")
    report.add("PREFLIGHT", "config_check", view.raw(E["config"]) == "ok", view.raw(E["config"]))
    report.add("PREFLIGHT", "sanity_check", view.raw(E["sanity"]) == "ok", view.raw(E["sanity"]))

    options = view.attr(E["mode"], "options", [])
    report.add(
        "PREFLIGHT",
        "mode_options",
        isinstance(options, list) and len(options) >= 2,
        f"options={options}",
    )
    auto = automation_map(view)
    report.add("PREFLIGHT", "plan_freeze_found", "plan_freeze" in auto, str(auto.get("plan_freeze")))
    report.add(
        "PREFLIGHT", "session_manager_found", "session_manager" in auto, str(auto.get("session_manager"))
    )
    if execute:
        report.add(
            "SAFETY",
            "physical_writer_found",
            "single_writer" in auto,
            str(auto.get("single_writer")),
        )
        session = view.raw(E["session"])
        safe_session = session in {"closed", "armed", "done"}
        report.add(
            "SAFETY",
            "session_not_active",
            safe_session,
            f"session={session}; erlaubt=closed/armed/done",
        )
        report.add(
            "SAFETY",
            "risk_not_active",
            view.raw(E["risk"]) != "on",
            f"risk={view.raw(E['risk'])}",
        )
        report.add(
            "SAFETY",
            "evcc_override_not_active",
            view.raw(E["evcc"]) != "on",
            f"evcc={view.raw(E['evcc'])}",
        )
        report.add(
            "SAFETY",
            "critical_deficit_not_latched",
            view.raw(E["critical_latch"]) != "on",
            f"critical_latch={view.raw(E['critical_latch'])}",
        )
        master = view.raw(E["master"])
        desired = view.num(E["desired"], 0.0) or 0.0
        safe_managed_command = desired <= 0.0 or master == "off"
        report.add(
            "SAFETY",
            "no_active_managed_charge_command",
            safe_managed_command,
            (
                f"master={master}, desired_charge_limit_w={desired}; "
                "bei Master aus ist der Fail-open-Wert zulässig"
            ),
        )
        active_ts = integer(view, E["active"])
        now_ts = int(datetime.now(tz).timestamp())
        start_safe = session != "armed" or active_ts <= 0 or active_ts > now_ts + 300
        report.add(
            "SAFETY",
            "not_within_five_minutes_of_start",
            start_safe,
            f"active_start={local_time(active_ts, tz)}",
        )
    return view, tz, auto


def read_only_phase(client: HAClient, report: Report, tz: ZoneInfo) -> None:
    view = View(client.states())
    mode = view.raw(E["mode"])
    try:
        data, checks = evaluate_mode(view, mode, tz)
    except Exception as exc:
        report.add("READ_ONLY", "current_mode_math", False, str(exc))
        return
    report.modes.append(data)
    for name, ok, detail in checks:
        # Replanning checks only make sense after a controlled mode-change trigger.
        if name in {"stored_start_replanned", "active_start_matches_plan"}:
            report.add("READ_ONLY", name, None, "nur mit --execute geprüft")
        else:
            report.add("READ_ONLY", name, ok, detail)


def session_expected(view: View, mode: str, tz: ZoneInfo) -> str:
    enabled = view.raw(E["master"]) == "on"
    cfg_ok = view.raw(E["config"]) == "ok"
    sanity_ok = view.raw(E["sanity"]) == "ok"
    evcc = view.raw(E["evcc"]) == "on"
    soe = view.num(E["soe"], 0.0) or 0.0
    low = view.num(E["low_floor"], 25.0) or 25.0
    need = view.num(E["needed"], 0.0) or 0.0
    lifetime_reached = view.raw(E["lifetime_latch"]) == "on"
    now_ts = int(datetime.now(tz).timestamp())
    planned = parse_datetime_state(view.raw(E["planned"]), tz)
    candidate = integer(view, E["candidate"])
    end_ts = integer(view, E["end"])
    end_grace = integer(view, E["end_grace"])
    min_hour = view.num(E["mode_min"], 0.0) or 0.0
    min_ts = hour_timestamp(datetime.now(tz), min_hour)
    planned_valid = planned >= min_ts and planned < end_ts
    candidate_valid = candidate >= min_ts and candidate < end_ts

    if not enabled:
        return "closed"
    if evcc:
        return "evcc_override"
    if not cfg_ok or not sanity_ok:
        return "risk"
    if soe <= low:
        return "low_soc"
    if mode == "Eigenverbrauch maximieren":
        return "open"
    if mode == "Akku schonen" and lifetime_reached:
        return "done"
    if end_ts > 0 and now_ts >= end_ts:
        return "done"
    if planned_valid and planned > 0 and now_ts >= planned:
        return "battery_full_open" if need <= 0.05 else "open"
    if planned_valid and planned > 0:
        return "armed"
    if candidate_valid:
        return "armed"
    return "closed"


def execute_phase(
    client: HAClient,
    report: Report,
    original: View,
    tz: ZoneInfo,
    auto: dict[str, str],
    timeout: float,
) -> None:
    options = list(original.attr(E["mode"], "options", []))
    original_mode = original.raw(E["mode"])
    order = [mode for mode in options if mode != original_mode] + [original_mode]
    original_values = {
        "mode": original_mode,
        "session": original.raw(E["session"]),
        "planned": original.raw(E["planned"]),
        "master": original.raw(E["master"]),
        "lifetime_latch": original.raw(E["lifetime_latch"]),
        "critical_latch": original.raw(E["critical_latch"]),
        "actual_limit": original.num(E["actual_limit"]),
    }
    controlled_keys = [key for key in AUTOMATION_IDS if key in auto]
    original_automation = {key: original.raw(auto[key]) for key in controlled_keys}
    recovery_path = write_recovery_snapshot(original, auto, original_automation)
    report.add("SAFETY", "recovery_snapshot", True, str(recovery_path))
    isolated = False

    try:
        # Physical isolation happens before any helper or mode is changed.
        for key in ("single_writer", "writer_close_bypass", "master_off_defaults"):
            if key in auto:
                set_automation(client, auto[key], "off")
        isolated = True
        report.add("SAFETY", "writer_isolation", True, "bekannte physische Writer sind aus")

        for key in (
            "session_manager", "latch_reset", "target_latch", "latch_repair",
            "critical_latch", "critical_reset",
        ):
            if key in auto:
                set_automation(client, auto[key], "off")
        set_automation(client, auto["plan_freeze"], "on")

        if original.exists(E["lifetime_latch"]):
            set_boolean(client, E["lifetime_latch"], "off")
        if original.exists(E["critical_latch"]):
            set_boolean(client, E["critical_latch"], "off")
        if original.raw(E["master"]) != "on":
            set_boolean(client, E["master"], "on")
        select_option(client, E["session"], "closed")

        for mode in order:
            select_option(client, E["session"], "closed")
            select_option(client, E["mode"], mode)
            stable = 0
            latest_data: dict[str, Any] | None = None
            latest_checks: list[tuple[str, bool, str]] = []
            deadline = time.monotonic() + timeout
            while time.monotonic() < deadline:
                view = View(client.states())
                try:
                    data, checks = evaluate_mode(view, mode, tz)
                except Exception:
                    stable = 0
                    time.sleep(1)
                    continue
                latest_data, latest_checks = data, checks
                if all(ok for _, ok, _ in checks):
                    stable += 1
                    if stable >= 2:
                        break
                else:
                    stable = 0
                time.sleep(1)

            if latest_data is None:
                report.add("MODE_SWEEP", f"{mode}:evaluation", False, "keine auswertbaren Werte")
                continue
            latest_data["expected_candidate_local"] = local_time(
                int(latest_data["expected_candidate_timestamp"] or 0), tz
            )
            latest_data["reported_candidate_local"] = local_time(
                int(latest_data["reported_candidate_timestamp"] or 0), tz
            )
            latest_data["stored_local"] = local_time(int(latest_data["stored_timestamp"] or 0), tz)
            latest_data["active_local"] = local_time(int(latest_data["active_timestamp"] or 0), tz)
            report.modes.append(latest_data)
            for name, ok, detail in latest_checks:
                report.add("MODE_SWEEP", f"{mode}:{name}", ok, detail)

        # Cross-mode relation: actual deltas must equal independently calculated deltas.
        usable = [m for m in report.modes if m.get("expected_candidate_timestamp")]
        for left, right in zip(usable, usable[1:]):
            expected_delta = right["expected_candidate_timestamp"] - left["expected_candidate_timestamp"]
            actual_delta = right["reported_candidate_timestamp"] - left["reported_candidate_timestamp"]
            report.add(
                "CROSS_MODE",
                f"{left['mode']} -> {right['mode']}",
                abs(expected_delta - actual_delta) <= 2,
                f"actual_delta_s={actual_delta}, expected_delta_s={expected_delta}",
            )

        # Session-manager phase.  The writer stays isolated throughout.
        for mode in order:
            set_automation(client, auto["session_manager"], "off")
            select_option(client, E["session"], "closed")
            select_option(client, E["mode"], mode)
            before = wait_for(
                client,
                lambda v, m=mode: v.raw(E["effective_mode"]) == m,
                timeout,
            )
            expected = session_expected(before, mode, tz)
            set_automation(client, auto["session_manager"], "on")
            service_entity(client, "automation", "trigger", auto["session_manager"], skip_condition=False)
            after = wait_for(client, lambda v, e=expected: v.raw(E["session"]) == e, timeout)
            actual = after.raw(E["session"])
            record = {
                "mode": mode,
                "expected_session": expected,
                "actual_session": actual,
                "needed_kwh": after.num(E["needed"]),
                "candidate_timestamp": integer(after, E["candidate"]),
            }
            report.session_modes.append(record)
            report.add(
                "SESSION_MANAGER",
                f"{mode}:state",
                actual == expected,
                f"actual={actual}, expected={expected}",
            )
            set_automation(client, auto["session_manager"], "off")

        after_limit = View(client.states()).num(E["actual_limit"])
        if original_values["actual_limit"] is None or after_limit is None:
            report.warn("SAFETY", "physical_limit_unchanged", "Ist-Limit-Sensor nicht numerisch verfügbar")
        else:
            report.add(
                "SAFETY",
                "physical_limit_unchanged",
                close(original_values["actual_limit"], after_limit, 0.1),
                f"before={original_values['actual_limit']}, after={after_limit}",
            )

    finally:
        cleanup_errors: list[str] = []

        def safe(label: str, fn: Callable[[], None]) -> None:
            try:
                fn()
            except Exception as exc:  # cleanup must continue
                cleanup_errors.append(f"{label}: {exc}")

        # Keep every physical writer disabled until all helpers are restored.
        if isolated:
            if "session_manager" in auto:
                safe("session manager off", lambda: set_automation(client, auto["session_manager"], "off"))
            if "plan_freeze" in auto:
                safe("plan freeze off", lambda: set_automation(client, auto["plan_freeze"], "off"))

            safe("restore mode", lambda: select_option(client, E["mode"], original_values["mode"]))
            safe("restore planned start", lambda: set_datetime(client, E["planned"], original_values["planned"]))
            safe("restore session", lambda: select_option(client, E["session"], original_values["session"]))
            if original.exists(E["lifetime_latch"]):
                safe(
                    "restore lifetime latch",
                    lambda: set_boolean(client, E["lifetime_latch"], original_values["lifetime_latch"]),
                )
            if original.exists(E["critical_latch"]):
                safe(
                    "restore critical latch",
                    lambda: set_boolean(client, E["critical_latch"], original_values["critical_latch"]),
                )
            safe("restore master", lambda: set_boolean(client, E["master"], original_values["master"]))

            # Restore non-physical automations first, physical writer last.
            for key in controlled_keys:
                if key in {"single_writer", "writer_close_bypass", "master_off_defaults"}:
                    continue
                safe(
                    f"restore automation {key}",
                    lambda k=key: set_automation(client, auto[k], original_automation[k]),
                )
            for key in ("master_off_defaults", "writer_close_bypass", "single_writer"):
                if key in original_automation:
                    safe(
                        f"restore automation {key}",
                        lambda k=key: set_automation(client, auto[k], original_automation[k]),
                    )

        time.sleep(1)
        restored = View(client.states())
        mode_ok = restored.raw(E["mode"]) == original_values["mode"]
        master_ok = restored.raw(E["master"]) == original_values["master"]
        planned_now = parse_datetime_state(restored.raw(E["planned"]), tz)
        planned_old = parse_datetime_state(original_values["planned"], tz)
        planned_ok = abs(planned_now - planned_old) <= 2
        report.cleanup_ok = not cleanup_errors and mode_ok and master_ok and planned_ok
        report.add(
            "CLEANUP",
            "original_state_restored",
            report.cleanup_ok,
            f"mode={mode_ok}, master={master_ok}, planned={planned_ok}, errors={cleanup_errors}",
        )
        if report.cleanup_ok:
            recovery_path.unlink(missing_ok=True)


def render_text(report: Report, execute: bool, tz_name: str) -> str:
    lines = [
        VERSION,
        f"generated_utc: {datetime.now(ZoneInfo('UTC')).isoformat()}",
        f"timezone: {tz_name}",
        f"execute_mode_switches: {str(execute).lower()}",
        "privacy: no_token_no_host_no_entity_mappings",
        "",
    ]
    phases: list[str] = []
    for check in report.checks:
        if check.phase not in phases:
            phases.append(check.phase)
    for phase in phases:
        lines.append(f"[{phase}]")
        for check in [item for item in report.checks if item.phase == phase]:
            lines.append(f"{check.status}: {check.name}: {check.detail}")
        lines.append("")

    if report.modes:
        lines.append("[MODE_VALUES]")
        for mode in report.modes:
            lines.extend(
                [
                    f"mode: {mode.get('mode')}",
                    "  targets_pct: "
                    f"normal={mode.get('normal_target_pct')} "
                    f"resilience={mode.get('resilience_target_pct')} "
                    f"effective={mode.get('effective_target_pct')} "
                    f"compatibility={mode.get('compatibility_target_pct')}",
                    "  need_kwh: "
                    f"reported={mode.get('reported_needed_kwh')} expected={mode.get('expected_needed_kwh')}",
                    "  required_min: "
                    f"reported={mode.get('reported_required_min')} expected={mode.get('expected_required_min')}",
                    "  mode_hours: "
                    f"min={mode.get('reported_min_hour')} end={mode.get('reported_end_hour')} "
                    f"buffer={mode.get('reported_buffer_min')}",
                    "  leads_min: "
                    f"weather={mode.get('weather_lead_min')} load={mode.get('load_lead_min')} "
                    f"adaptive={mode.get('adaptive_lead_min')} live_gap={mode.get('live_gap_lead_min')}",
                    "  start: "
                    f"expected={mode.get('expected_candidate_local', mode.get('expected_candidate_timestamp'))} "
                    f"candidate={mode.get('reported_candidate_local', mode.get('reported_candidate_timestamp'))} "
                    f"stored={mode.get('stored_local', mode.get('stored_timestamp'))} "
                    f"active={mode.get('active_local', mode.get('active_timestamp'))}",
                    f"  source={mode.get('selected_source')} window_valid={mode.get('window_valid')}",
                ]
            )
        lines.append("")

    passed = sum(c.status == "PASS" for c in report.checks)
    failed = sum(c.status == "FAIL" for c in report.checks)
    warned = sum(c.status == "WARN" for c in report.checks)
    skipped = sum(c.status == "SKIP" for c in report.checks)
    lines.extend(
        [
            "[RESULT]",
            f"checks_total: {len(report.checks)}",
            f"checks_passed: {passed}",
            f"checks_failed: {failed}",
            f"checks_warned: {warned}",
            f"checks_skipped: {skipped}",
            f"cleanup_ok: {report.cleanup_ok if execute else 'not_required'}",
            f"overall: {'PASS' if failed == 0 and (not execute or report.cleanup_ok) else 'FAIL'}",
        ]
    )
    return "\n".join(lines) + "\n"


def save_report(report: Report, text: str, execute: bool, tz_name: str) -> tuple[Path, Path]:
    share = Path("/share") if Path("/share").is_dir() else Path("/tmp")
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    txt_path = share / f"SE_NF_FULL_MODE_ACCEPTANCE_{stamp}.txt"
    json_path = share / f"SE_NF_FULL_MODE_ACCEPTANCE_{stamp}.json"
    txt_path.write_text(text, encoding="utf-8")
    payload = {
        "version": VERSION,
        "generated_utc": datetime.now(ZoneInfo("UTC")).isoformat(),
        "timezone": tz_name,
        "execute_mode_switches": execute,
        "privacy": "no_token_no_host_no_entity_mappings",
        "checks": [vars(c) for c in report.checks],
        "modes": report.modes,
        "session_modes": report.session_modes,
        "cleanup_ok": report.cleanup_ok,
        "overall": "PASS" if not report.failures and (not execute or report.cleanup_ok) else "FAIL",
    }
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return txt_path, json_path


def self_test() -> int:
    tz = ZoneInfo("Europe/Berlin")
    now = datetime.now(tz)
    assert hour_timestamp(now, 14.25) == int(now.replace(hour=14, minute=15, second=0, microsecond=0).timestamp())
    assert parse_datetime_state("2026-07-17 16:36:00", tz) > 0
    assert close(59.2, 59.21, 0.02)
    print(f"{VERSION} SELF_TEST PASS")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Writer isolieren und alle Modi real durchschalten; Zustand wird danach wiederhergestellt.",
    )
    parser.add_argument("--timeout", type=float, default=35.0, help="Wartezeit je Umschaltung in Sekunden.")
    parser.add_argument("--self-test", action="store_true", help="Nur interne Mathematik testen.")
    parser.add_argument(
        "--recover",
        nargs="?",
        const=str(RECOVERY_PATH),
        metavar="DATEI",
        help="Nach hartem Abbruch den gesicherten HA-Ausgangszustand wiederherstellen.",
    )
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    if args.recover:
        try:
            client = HAClient()
            path = Path(args.recover)
            if not path.is_file():
                raise HAError(f"Recovery-Datei fehlt: {path}")
            recover_snapshot(client, path)
            print(f"{VERSION} RECOVERY PASS")
            print("Ausgangszustand wiederhergestellt; Recovery-Datei entfernt.")
            return 0
        except Exception as exc:
            print(f"{VERSION} RECOVERY FAIL: {type(exc).__name__}: {exc}", file=sys.stderr)
            return 2

    report = Report()
    exit_code = 1
    try:
        client = HAClient()
        static_scan(report)
        original, tz, auto = preflight(client, report, args.execute)
        if report.failures:
            report.notes.append("Preflight fehlgeschlagen; kein aktiver Umschalttest ausgeführt.")
        elif args.execute:
            execute_phase(client, report, original, tz, auto, args.timeout)
        else:
            read_only_phase(client, report, tz)
        tz_name = str(tz)
    except Exception as exc:
        report.add("FATAL", "exception", False, f"{type(exc).__name__}: {exc}")
        report.notes.append(traceback.format_exc(limit=8))
        tz_name = "unknown"

    text = render_text(report, args.execute, tz_name)
    print(text, end="")
    try:
        txt_path, json_path = save_report(report, text, args.execute, tz_name)
        print(f"report_text: {txt_path}")
        print(f"report_json: {json_path}")
    except OSError as exc:
        print(f"report_save_error: {exc}")

    if not report.failures and (not args.execute or report.cleanup_ok):
        exit_code = 0
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
