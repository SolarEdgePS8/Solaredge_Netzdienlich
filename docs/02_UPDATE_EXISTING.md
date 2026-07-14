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

Bei geklontem Repository:

```bash
cd /config/repos/Solaredge_Netzdienlich
git pull --ff-only
```

## 3. Neue Package-Dateien kopieren

```bash
./scripts/install_package.sh
ha core check
```

Nur bei erfolgreichem Check:

```bash
ha core restart
```

## 4. Bestehende Site-Konfiguration nicht überschreiben

`apply_site_config.sh` ist primär für die Erstinstallation. Bei einem Update wird es nur erneut ausgeführt, wenn neue Mapping-Helfer hinzugekommen sind oder Entity-IDs bewusst geändert werden sollen.

Neu in v2.9.6:

```text
input_text.se_nf_discharge_limit_entity
```

Dieser Helfer ist optional. Er wird nur benötigt, wenn beim Ausschalten des Masters zusätzlich ein SolarEdge-Discharge-Limit auf den Defaultwert zurückgesetzt werden soll.

## 5. Audit ausführen

```bash
./scripts/install_audit_suite.sh
/share/se_nf_release_audit_v296/run_readonly.sh
/share/se_nf_release_audit_v296/se_nf_manifest_audit.py
```

## 6. Changelog lesen

Siehe [`CHANGELOG.md`](../CHANGELOG.md).
