# Safety and Writer

## Grundprinzip

Der Writer soll nur schreiben, wenn:

- Master aktiv ist
- Config Check ok ist
- Sanity Check ok ist
- kein Write-Lock aktiv ist
- Cooldown eingehalten wird
- Zielwert vom Istwert ausreichend abweicht

## Wichtige Writer-/Safety-Entities

```text
input_boolean.se_netzdienlich_enabled
sensor.se_nf_config_check
sensor.se_nf_sanity_check
sensor.se_nf_writer_mode
sensor.se_nf_charge_limit_target
sensor.se_nf_desired_target
sensor.se_nf_charge_limit_actual
number.solaredge_i1_storage_charge_limit
binary_sensor.se_nf_write_lock_active
input_datetime.se_nf_write_lock_until
input_number.se_nf_write_cooldown_s
input_number.se_nf_write_lock_s
input_number.se_nf_write_min_delta_w
```

## Safe Default

Bei unsicherem Zustand soll das Package geschlossen bleiben oder schließen:

```text
charge_limit_target = 0
desired_target = 0
```

## Prüfung

```bash
for e in \
sensor.se_nf_config_check \
sensor.se_nf_sanity_check \
sensor.se_nf_writer_mode \
sensor.se_nf_charge_limit_target \
sensor.se_nf_desired_target \
sensor.se_nf_charge_limit_actual \
number.solaredge_i1_storage_charge_limit \
binary_sensor.se_nf_write_lock_active
do
  echo
  echo "### $e"
  curl -sS -H "Authorization: Bearer $SUPERVISOR_TOKEN" \
    "http://supervisor/core/api/states/$e"
done
```
