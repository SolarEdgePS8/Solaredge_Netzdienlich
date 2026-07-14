# Changelog

## v2.9.6

### YAML-Robustheit

- Sensoralter nutzt bevorzugt `last_reported` und fällt auf `last_updated` zurück.
- Behebt mögliche `battery_soe_stale`-Fehlalarme bei regelmäßig gemeldeten, aber unveränderten Sensorwerten.
- SolarEdge-Writer verbucht `last_write`, Write-Lock und `last_applied` erst nach erfolgreichem `number.set_value`.
- Harter `number.solaredge_i1_storage_charge_limit`-Trigger aus dem Haupt-Writer entfernt.
- Writer-Safety-Sidecar nutzt das konfigurierte Charge-Limit-Mapping.
- Optionales `input_text.se_nf_discharge_limit_entity` ergänzt.
- Hartes Hausverbrauchs-`initial` aus dem Planning-Helper entfernt, damit lokale Mappings Neustarts überleben.
- Fallback-Resolver akzeptieren einen gültigen ersten Wert von `0 W` und wechseln danach nicht zu einem späteren Kandidaten.
- Master-AUS-Defaults schreiben nur noch bei echter Abweichung und verhindern überlappende Läufe.

### Erstinstallation und Portierung

- Eine eindeutige Erstinstallationsanleitung.
- Eine separate Update-Anleitung.
- Site-Konfigurationsvorlage mit Pflicht-Mappings und einmaligen Startwerten.
- Discovery-Script für Power-, Energy-, Weather-, SoE- und SolarEdge-Kandidaten.
- `apply_site_config.sh` setzt Mappings, ohne den Master zu aktivieren.
- Erklärung von `_filtered`, `entity` und `entities`.
- Klare Unterscheidung zwischen Leistung in `W` und Energie in `kWh`.

### Repository-Aufräumen

- Doppelte First-Run-Skripte entfernt.
- Nur noch `scripts/run_first_checks.sh`.
- Audit-Python-Dateien verständlich dokumentiert.
- Dokumentation fortlaufend nummeriert.
- Backup-Dateien und alte Audit-Baks nicht im Release enthalten.

### GitHub Issues berücksichtigt

- Issue #1: Fresh-install Defaults, `battery_soe_stale`, gültiger `writer_mode=normal`.
- Issue #2: Modbus-Fehler und Writer-Bookkeeping nach erfolgreichem Write.
- Issue #3: PV-Mapping, `_filtered` und Fallback-Listen.
