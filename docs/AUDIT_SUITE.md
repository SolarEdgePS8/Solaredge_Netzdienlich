# Release-Audit-Suite

Die Audit-Suite liegt im Release unter:

```text
audit/
```

Für die Nutzung auf Home Assistant den Ordner nach `/share/se_nf_release_audit_v295/` kopieren.

## Read-only Audit

Ändert keine Werte.

```bash
/share/se_nf_release_audit_v295/run_readonly.sh
```

Prüft:

- `ha core check`
- Package-Dateien
- Duplicate `unique_id`
- Legacy-Referenzen
- kritische fehlende Abhängigkeiten
- Runtime-Plausibilität
- Config/Sanity/Writer-Zustand

Erwartung:

```text
GATE_STATIC_MAIN_CRITICAL: PASS
critical_main: 0
GATE_RUNTIME: PASS
runtime_fail_count: 0
```

## Manifest-Audit

Prüft nur die Release-Dateien:

```bash
/share/se_nf_release_audit_v295/se_nf_manifest_audit.py
```

Erwartung:

```text
critical_internal: 0
GATE_MANIFEST: PASS_OR_EXTERNAL_REVIEW
```

`PASS_OR_EXTERNAL_REVIEW` bedeutet: Package intern sauber, externe SolarEdge-Entities müssen auf der Zielinstanz geprüft werden.

## Safe-A/B-Test

Temporärer Funktionstest. Verändert nur `input_*` Helfer und stellt sie zurück.

```bash
/share/se_nf_release_audit_v295/run_safe_ab.sh
```

Der Test läuft nur bei ruhigem Zustand:

```text
input_select.se_nf_session_state = closed oder armed
sensor.se_nf_charge_limit_target = 0
sensor.se_nf_desired_target = 0
```

Er schreibt nicht direkt auf SolarEdge-Number-Entities.

## Reports

```text
/share/se_nf_release_audit_reports/<timestamp>/
```
