# 04 – Audit-Suite

Der Ordner `audit/` enthält Prüfprogramme. Die `.py`-Dateien sind keine Home-Assistant-Integrationen und werden nicht nach `/config/custom_components` kopiert.

## `run_readonly.sh`

Der Standardtest für Erstinstallation und Update.

Er prüft unter anderem:

- `ha core check`,
- kritische fehlende Abhängigkeiten,
- doppelte `unique_id`,
- Runtime-Plausibilität,
- Config-/Sanity-/Writer-Zustand.

Er verändert keine Helfer und schreibt nicht auf SolarEdge.

## `se_nf_manifest_audit.py`

Prüft nur die vier Dateien des Release-Manifests. Damit werden Fehler aus fremden, nicht zum Release gehörenden Packages ausgeblendet.

## `run_safe_ab.sh`

Temporärer A/B-Test für Planungsparameter. Er verändert ausgewählte `input_*`-Helfer und stellt sie wieder her. Er läuft nur bei ruhigem Zustand und schreibt nicht direkt auf SolarEdge.

Für eine normale Erstinstallation ist der Safe-A/B-Test nicht zwingend erforderlich.

## `run_all.sh`

Kombiniert Read-only und Safe-A/B. Nicht als ersten Test verwenden.

## Installation

```bash
./scripts/install_audit_suite.sh
```

## Standardaufruf

```bash
/share/se_nf_release_audit_v296/run_readonly.sh
/share/se_nf_release_audit_v296/se_nf_manifest_audit.py
```
