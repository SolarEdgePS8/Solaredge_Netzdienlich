# Troubleshooting

## `sensor.se_nf_config_check` ist nicht `ok`

Prüfen:

```text
input_text.se_nf_charge_limit_entity
input_text.se_nf_battery_soe_entity
input_text.se_nf_backup_reserve_entity
```

Die dort eingetragenen Entities müssen existieren und gültige Werte liefern.

## `sensor.se_nf_sanity_check` ist nicht `ok`

Mögliche Ursachen:

- Charge-Limit-Entity fehlt
- Akku-SoE fehlt
- Backup-Reserve fehlt
- Ziel-SoC unplausibel
- Sensoren unavailable
- Sensorwerte zu alt

## Wetter wirkt nicht

Prüfen:

```text
input_boolean.se_nf_weather_planning_enabled
input_number.se_nf_weather_current_weight_pct
input_number.se_nf_weather_max_lead_min
input_text.se_nf_weather_entity
sensor.se_nf_weather_planning_factor_today
sensor.se_nf_weather_lead_minutes
```

Bei gutem Wetter ist `Weather Lead = 0 min` korrekt.

## Startzeit wirkt zu spät

Prüfen:

```text
input_number.se_nf_lifetime_latest_finish_hour
input_number.se_nf_lifetime_start_safety_buffer_min
input_number.se_nf_start_safety_buffer_min
input_number.se_nf_weather_max_lead_min
input_number.se_nf_coverage_lead_max_min
```

Im Modus `Akku schonen` ist besonders relevant:

```text
input_number.se_nf_lifetime_latest_finish_hour
input_number.se_nf_lifetime_start_safety_buffer_min
```

## Keine Ladung nötig / Akku voll

Dieser Zustand ist gültig:

```text
Heute keine Ladung nötig · Akku voll
Erledigt · Tagesfenster beendet
```

Das ist kein Fehler, wenn der Akku bereits über Ziel liegt.

## Safe-A/B bricht ab

Das ist gewollt, wenn nicht sicher getestet werden kann.

Erwartet:

```text
Session closed/armed
Target 0
Desired 0
```
