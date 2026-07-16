# 02 – Update einer bestehenden Installation

Diese Anleitung gilt, wenn das Package bereits läuft.

## 1. Bestehende Dateien sichern

```bash
TS="$(date +%Y%m%d_%H%M%S)"
mkdir -p "/share/se_nf_update_backup_$TS"
cp /config/packages/solaredge_netzdienlich.yaml "/share/se_nf_update_backup_$TS/"
cp /config/packages/se_nf_07_writer_safety.yaml "/share/se_nf_update_backup_$TS/"
cp /config/packages/se_nf_08_planning_helpers.yaml "/share/se_nf_update_backup_$TS/"
cp /config/packages/se_nf_09_lifetime_target_helpers.yaml "/share/se_nf_update_backup_$TS/"
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

`apply_site_config.sh` wird nur erneut ausgeführt, wenn Entity-IDs oder Startwerte bewusst geändert werden sollen. In v2.9.7 können leere optionale Variablen vorhandene alte optionale Helper-Mappings ausdrücklich entfernen.

Neu bzw. präzisiert in v2.9.7:

```text
ACTUAL_PV_TODAY_ENTITIES=
DAILY_CONSUMPTION_ENTITY=
PV_ACTUAL_METER_SOURCE_ENTITY=
EVCC_BATTERY_MODE_ENTITY=
```

Details: [`03_ENTITY_MAPPING.md`](03_ENTITY_MAPPING.md).

## 5. Änderungen aus v2.9.7 prüfen

- Issue #4: PV-Tagesertrag, Tagesverbrauch, Gesamtzähler und EVCC-Rückkanal.
- Issue #5: Startkandidat, gespeicherter Start, aktiver Start und Fensterende.
- Dashboard: Ordner [`dashboard/`](../dashboard/).

Ein Zeitfenster ist nur plausibel, wenn der Start vor dem Ende liegt.

## 6. Audit ausführen

```bash
./scripts/install_audit_suite.sh
/share/se_nf_release_audit/run_readonly.sh
/share/se_nf_release_audit/se_nf_manifest_audit.py
```

## 7. Changelog lesen

Siehe [`CHANGELOG.md`](../CHANGELOG.md).
