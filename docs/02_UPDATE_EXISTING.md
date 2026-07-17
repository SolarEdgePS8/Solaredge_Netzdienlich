# 02 – Update einer bestehenden Installation

Diese Anleitung gilt, wenn das Package bereits läuft.

## 1. Bestehende Dateien sichern

```bash
TS="$(date +%Y%m%d_%H%M%S)"
mkdir -p "/share/se_nf_update_backup_$TS"
cp /config/packages/solaredge_netzdienlich.yaml "/share/se_nf_update_backup_$TS/"
cp /config/packages/se_nf_07_writer_safety.yaml "/share/se_nf_update_backup_$TS/"
cp /config/packages/se_nf_08_planning_helpers.yaml "/share/se_nf_update_backup_$TS/"
cp /config/packages/se_nf_09_lifetime_target_helpers.yaml "/share/se_nf_update_backup_$TS/" 2>/dev/null || true
cp /config/packages/se_nf_10_dynamic_night_forecast.yaml "/share/se_nf_update_backup_$TS/" 2>/dev/null || true
cp /config/packages/se_nf_13_resilience_target.yaml "/share/se_nf_update_backup_$TS/" 2>/dev/null || true
cp /config/se_nf_load_forecast_7d_cached.py "/share/se_nf_update_backup_$TS/" 2>/dev/null || true
cp /config/se_nf_night_forecast_7d.py "/share/se_nf_update_backup_$TS/" 2>/dev/null || true
cp /config/se_nf_daytime_forecast_7d.py "/share/se_nf_update_backup_$TS/" 2>/dev/null || true
```

## 2. Repository aktualisieren

```bash
cd /config/repos/Solaredge_Netzdienlich
git pull --ff-only
```

Alternativ das Release-ZIP in einen neuen Ordner entpacken.

## 3. Neue Package-Dateien kopieren

```bash
./scripts/install_package.sh
ha core check
```

Nur bei erfolgreichem Check:

```bash
ha core restart
```

## 4. Bestehende Site-Konfiguration erhalten

Die produktiven `input_text`, `input_number`, `input_boolean`, `input_select` und `input_datetime`-Werte bleiben bei einem normalen Package-Update erhalten.

`apply_site_config.sh` wird nur erneut ausgeführt, wenn Entity-IDs oder Startwerte bewusst geändert werden sollen. In v2.9.8 können leere optionale Variablen vorhandene alte optionale Helper-Mappings ausdrücklich entfernen.

Neu bzw. präzisiert in v2.9.8:

```text
ACTUAL_PV_TODAY_ENTITIES=
DAILY_CONSUMPTION_ENTITY=
PV_ACTUAL_METER_SOURCE_ENTITY=
EVCC_BATTERY_MODE_ENTITY=
BACKUP_RESERVE_ENTITY=
BACKUP_RESERVE_FALLBACK_PCT=0
```

Details: [`03_ENTITY_MAPPING.md`](03_ENTITY_MAPPING.md).

## 5. Änderungen aus v2.9.8 prüfen

- Issue #5: Zielpfad, Startkandidat, gespeicherter Start, aktiver Start und Fensterende.
- Issue #6: der bisher fehlende 7-Tage-Lastprognose-Helfer wird mitinstalliert.
- Akku schonen: dynamische Tag-/Nacht-Historie und resilientes 24-/48-h-Ziel.
- Backup: optionales Mapping mit konfigurierbarem Fallback für Anlagen ohne
  Backup-System.
- Dashboard: Ordner [`dashboard/`](../dashboard/).

Der Installer verschiebt das nicht mehr verwendete Parallel-Ziel-Sidecar
`se_nf_09_lifetime_target_helpers.yaml` sowie die Entwicklungs-Sidecars
`se_nf_11_dynamic_target_preview.yaml`, `se_nf_14_resilience_refresh.yaml` und
`se_nf_quiet_logging.yaml` in seinen Backup-Ordner. Dadurch bleibt nur ein
kanonischer Min-/Max-Zielpfad, nur eine
Refresh-Automation aktiv und allgemeine Home-Assistant-Logs werden nicht
unterdrückt.

Ein Zeitfenster ist nur plausibel, wenn der Start vor dem Ende liegt.

## 6. Audit ausführen

```bash
./scripts/install_audit_suite.sh
/share/se_nf_release_audit/run_readonly.sh
/share/se_nf_release_audit/se_nf_manifest_audit.py
```

## 7. Changelog lesen

Siehe [`CHANGELOG.md`](../CHANGELOG.md).
