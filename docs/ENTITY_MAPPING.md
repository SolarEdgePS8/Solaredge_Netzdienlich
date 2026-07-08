# Entity Mapping

## Übersicht

| Zweck | Input-Text-Helfer | Default |
|---|---|---|
| Charge Limit | `input_text.se_nf_charge_limit_entity` | `number.solaredge_i1_storage_charge_limit` |
| Akku-SoE | `input_text.se_nf_battery_soe_entity` | `sensor.solaredge_i1_b1_state_of_energy` |
| Backup Reserve | `input_text.se_nf_backup_reserve_entity` | `number.solaredge_i1_backup_reserve` |
| PV-Ist-Leistung | `input_text.se_nf_live_pv_power_entities` | `sensor.power_solar_generation,...` |
| Verbrauchsleistung | `input_text.se_nf_live_consumption_power_entities` | `sensor.power_consumption` |
| PV-Forecast jetzt | `input_text.se_nf_forecast_now_entity` | lokaler Forecast-Sensor |
| Wetter | `input_text.se_nf_weather_entity` | `weather.ps8` |
| Tagesverbrauch | `input_text.se_nf_daily_consumption_entity` | lokaler Tagesverbrauch |
| SQL DB Pfad | `input_text.se_nf_sql_db_path` | `/config/home-assistant_v2.db` |

## Mappings anzeigen

```bash
for e in \
input_text.se_nf_charge_limit_entity \
input_text.se_nf_battery_soe_entity \
input_text.se_nf_backup_reserve_entity \
input_text.se_nf_live_pv_power_entities \
input_text.se_nf_live_consumption_power_entities \
input_text.se_nf_forecast_now_entity \
input_text.se_nf_weather_entity \
input_text.se_nf_pv_today_remaining_entity \
input_text.se_nf_pv_today_total_entity \
input_text.se_nf_pv_tomorrow_entity \
input_text.se_nf_pv_overmorrow_entities \
input_text.se_nf_daily_consumption_entity \
input_text.se_nf_sql_db_path
do
  echo
  echo "### $e"
  curl -sS -H "Authorization: Bearer $SUPERVISOR_TOKEN" \
    "http://supervisor/core/api/states/$e"
done
```

## Mapping setzen

Beispiel Verbrauchssensor:

```bash
curl -sS -X POST \
  -H "Authorization: Bearer $SUPERVISOR_TOKEN" \
  -H "Content-Type: application/json" \
  http://supervisor/core/api/services/input_text/set_value \
  -d '{"entity_id":"input_text.se_nf_live_consumption_power_entities","value":"sensor.mein_hausverbrauch_w"}'
```

Beispiel Wetter:

```bash
curl -sS -X POST \
  -H "Authorization: Bearer $SUPERVISOR_TOKEN" \
  -H "Content-Type: application/json" \
  http://supervisor/core/api/services/input_text/set_value \
  -d '{"entity_id":"input_text.se_nf_weather_entity","value":"weather.home"}'
```
