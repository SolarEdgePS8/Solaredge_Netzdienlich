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

Prüft die fünf Package-Dateien und drei Runtime-Helfer des Release-Manifests.
Damit werden Fehler aus fremden, nicht zum Release gehörenden Packages
ausgeblendet.

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
/share/se_nf_release_audit/run_readonly.sh
/share/se_nf_release_audit/se_nf_manifest_audit.py
```

## Vollständige v2.9.8-Abnahme

Der Resilienztester ist read-only:

```bash
python3 validation/se_nf_resilience_acceptance_test.py
```

Der vollständige Modustester kann seine interne Mathematik ohne Änderungen
prüfen:

```bash
python3 validation/se_nf_full_mode_acceptance_test.py --self-test
```

`--execute` schaltet alle drei Modi kontrolliert durch. Der Tester isoliert
dabei bekannte physische Writer und stellt den Ausgangszustand wieder her. Er
darf nur bei ruhigem Zustand und nach einem erfolgreichen `ha core check`
ausgeführt werden:

Bei ausgeschaltetem Master ist der sichere Fail-open-Wert `5000 W` als
Startzustand zulässig. Die physischen Writer werden deaktiviert, bevor der
Tester den Master ausschließlich für seine internen Modusprüfungen einschaltet.

```bash
python3 validation/se_nf_full_mode_acceptance_test.py --execute
```

Nach einem harten Terminalabbruch kann – sofern eine Recovery-Datei angelegt
wurde – der gespeicherte Zustand wiederhergestellt werden:

```bash
python3 validation/se_nf_full_mode_acceptance_test.py --recover
```
