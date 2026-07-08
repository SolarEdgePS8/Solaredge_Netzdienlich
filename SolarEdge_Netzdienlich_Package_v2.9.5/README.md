# SolarEdge Netzdienlich Package v2.9.5

Home-Assistant-Package zur netzdienlichen SolarEdge-Speichersteuerung mit Planungslogik, Wettergewichtung, PV-/Verbrauchsprognose, Akku-Schonen-Modus, Safety-/Writer-Logik und integrierter Release-Audit-Suite.

Dieses Release ist als **portierbares Package-Bundle** gedacht. Es ist **kein HACS-Addon** und **keine Custom Integration**, sondern eine Sammlung von Home-Assistant-Package-Dateien für `/config/packages`.

## Ziel

Das Package soll den SolarEdge-Speicher nicht einfach immer sofort laden, sondern den Ladezeitpunkt anhand von Bedarf, PV-Prognose, Wetter, Akku-SoC, Ziel-SoC und Sicherheitsgrenzen planen.

Es kann insbesondere helfen bei:

- netzdienlicher Speichersteuerung
- später oder früher geplanter Speicherladung
- Akku-Schonen-Betrieb
- Wetter-basierter Startzeitkorrektur
- Vermeidung unnötiger Speicherladung
- Write-Safety gegen zu häufige oder falsche SolarEdge-Schreibbefehle
- Diagnose und Release-Audit vor produktiver Nutzung

## Enthaltene Struktur

```text
package/
  solaredge_netzdienlich.yaml
  se_nf_07_writer_safety.yaml
  se_nf_08_planning_helpers.yaml
  se_nf_09_lifetime_target_helpers.yaml

audit/
  se_nf_release_audit.py
  se_nf_manifest_audit.py
  run_readonly.sh
  run_safe_ab.sh
  run_all.sh
  README.txt

docs/
  INSTALL.md
  PORTING.md
  ENTITY_MAPPING.md
  FUNCTIONAL_OVERVIEW.md
  SAFETY_AND_WRITER.md
  AUDIT_SUITE.md
  TROUBLESHOOTING.md
  TEST_PROTOCOL_v2.9.5.md
  UPGRADE_FROM_OLDER_RELEASES.md

github/
  RELEASE_BODY_v2.9.5.md
  TAG_AND_TITLE.txt
  CHECKLIST_BEFORE_PUBLISH.md

examples/
  configuration_yaml_packages.md
  first_run_checks.sh

scripts/
  install_package_files.sh
  run_first_checks.sh

validation/
  RELEASE_GATE_SUMMARY.md
  BUNDLE_FILE_HASHES_SHA256.txt
```

## Wichtiges Sicherheitsprinzip

Das Package kann SolarEdge-Setpoints schreiben, wenn es aktiv ist.

Vor produktiver Aktivierung müssen daher zwingend geprüft werden:

- korrekte SolarEdge Charge-Limit-Entity
- korrekte Akku-SoE-Entity
- korrekte Backup-Reserve-Entity
- lokale PV-Ist-Leistung
- lokale Verbrauchsleistung
- Wetter-Entity
- PV-Prognose-Entities
- `sensor.se_nf_config_check = ok`
- `sensor.se_nf_sanity_check = ok`

## Minimaler Ablauf für neue Installationen

1. Dateien aus `package/` nach `/config/packages/` kopieren.
2. Packages in `configuration.yaml` aktivieren.
3. `ha core check` ausführen.
4. Home Assistant neu starten.
5. Master-Schalter zunächst aus lassen.
6. Entity-Mappings anpassen.
7. Read-only-Audit ausführen.
8. Erst nach erfolgreichem Audit produktiv aktivieren.

## Release-Gates v2.9.5

Letzter geprüfter Stand:

```text
GATE_STATIC_MAIN_CRITICAL: PASS
critical_main: 0
GATE_RUNTIME: PASS
runtime_fail_count: 0
GATE_MANIFEST: PASS_OR_EXTERNAL_REVIEW
critical_internal: 0
```

`PASS_OR_EXTERNAL_REVIEW` ist korrekt, weil SolarEdge-Entities und lokale Mapping-Entities auf jeder Home-Assistant-Instanz individuell geprüft werden müssen.
