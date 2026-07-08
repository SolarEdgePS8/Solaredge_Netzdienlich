# SolarEdge Netzdienlich Package v2.9.5

## Highlights

- Wetter-Final-Faktor wirkt jetzt korrekt auf Weather Lead Minutes und Startzeitlogik.
- Akku-schonen-Startpuffer wirkt jetzt korrekt über den modusabhängigen Sensor.
- Critical-Deficit-/Early-Open-Guard wurde von alten unavailable Legacy-Sensoren entkoppelt.
- Live-Verbrauchsleistung ist jetzt über `input_text.se_nf_live_consumption_power_entities` konfigurierbar.
- Release-Audit-Suite für Static-, Runtime-, Manifest-, Portability- und Safe-A/B-Checks integriert.

## Release-Gates

```text
GATE_STATIC_MAIN_CRITICAL: PASS
critical_main: 0
GATE_RUNTIME: PASS
runtime_fail_count: 0
GATE_MANIFEST: PASS_OR_EXTERNAL_REVIEW
critical_internal: 0
```

## Enthaltene Package-Dateien

```text
package/solaredge_netzdienlich.yaml
package/se_nf_07_writer_safety.yaml
package/se_nf_08_planning_helpers.yaml
package/se_nf_09_lifetime_target_helpers.yaml
```

## Wichtig für neue Installationen

Nach Installation müssen lokale Entity-Mappings geprüft werden:

```text
input_text.se_nf_charge_limit_entity
input_text.se_nf_battery_soe_entity
input_text.se_nf_backup_reserve_entity
input_text.se_nf_live_pv_power_entities
input_text.se_nf_live_consumption_power_entities
input_text.se_nf_forecast_now_entity
input_text.se_nf_weather_entity
```

Siehe:

```text
docs/PORTING.md
docs/ENTITY_MAPPING.md
docs/AUDIT_SUITE.md
```

## Audit

Read-only Audit:

```bash
/share/se_nf_release_audit_v295/run_readonly.sh
```

Manifest Audit:

```bash
/share/se_nf_release_audit_v295/se_nf_manifest_audit.py
```

Safe A/B Test:

```bash
/share/se_nf_release_audit_v295/run_safe_ab.sh
```
