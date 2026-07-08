# Quickstart

## 1. Package-Dateien kopieren

Kopiere diese Dateien nach `/config/packages/`:

```text
package/solaredge_netzdienlich.yaml
package/se_nf_07_writer_safety.yaml
package/se_nf_08_planning_helpers.yaml
package/se_nf_09_lifetime_target_helpers.yaml
```

## 2. Packages aktivieren

In `configuration.yaml`:

```yaml
homeassistant:
  packages: !include_dir_named packages
```

## 3. Check und Neustart

```bash
ha core check
```

Nur wenn der Check erfolgreich ist:

```bash
ha core restart
```

## 4. Erste Prüfung

```bash
for e in \
sensor.se_nf_config_check \
sensor.se_nf_sanity_check \
sensor.se_nf_today_charge_window \
sensor.se_nf_decision_reason \
sensor.se_nf_writer_mode \
sensor.se_nf_charge_limit_target \
sensor.se_nf_charge_limit_actual \
input_boolean.se_netzdienlich_enabled
do
  echo
  echo "### $e"
  curl -sS -H "Authorization: Bearer $SUPERVISOR_TOKEN" \
    "http://supervisor/core/api/states/$e"
done
```

Erwartung:

```text
sensor.se_nf_config_check = ok
sensor.se_nf_sanity_check = ok
sensor.se_nf_writer_mode = idle
```
