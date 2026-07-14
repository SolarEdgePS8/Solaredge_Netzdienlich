# SolarEdge Netzdienlich Package v2.9.6

## Schwerpunkt

Dieses Release verbessert die Nutzbarkeit auf **neuen und fremden Home-Assistant-Instanzen**.

## YAML-Fixes

- Sensoralter verwendet jetzt `last_reported` mit `last_updated`-Fallback.
- Writer-Bookkeeping erfolgt erst nach erfolgreichem SolarEdge-Service-Call.
- Harte Charge-Limit-Referenzen in Writer/Close-Bypass wurden durch Mappings ersetzt.
- Optionales Discharge-Limit-Mapping ergänzt.
- Lokales Hausverbrauchs-Mapping wird nicht mehr durch einen festen `initial`-Wert überschrieben.
- Fallback-Listen behandeln `0 W` korrekt als gültigen ersten Wert.
- Master-AUS-Defaults vermeiden redundante Modbus-Schreibvorgänge und parallele Läufe.

## Neue, vereinfachte Installation

- `docs/01_FIRST_INSTALL.md`
- `docs/02_UPDATE_EXISTING.md`
- `config/site_config.env.example`
- `scripts/discover_entities.py`
- `scripts/apply_site_config.sh`
- genau ein First-Run-Check: `scripts/run_first_checks.sh`

## Audit

```text
GATE_STATIC_MAIN_CRITICAL: PASS
critical_main: 0
GATE_RUNTIME: PASS
runtime_fail_count: 0
GATE_MANIFEST: PASS_OR_EXTERNAL_REVIEW
critical_internal: 0
```

## Wichtig

Vor Aktivierung müssen lokale Entity-IDs in `config/site_config.env` eingetragen und das Read-only-Audit ausgeführt werden. Das Package ist eine Home-Assistant-Package-Sammlung und keine HACS-Integration.
