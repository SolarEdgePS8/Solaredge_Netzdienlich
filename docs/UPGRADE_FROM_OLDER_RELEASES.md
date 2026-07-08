# Upgrade von älteren Releases

## Von v2.9.4b / v2.9.4c auf v2.9.5

Neue zusätzliche Package-Dateien:

```text
se_nf_08_planning_helpers.yaml
se_nf_09_lifetime_target_helpers.yaml
```

Diese müssen zusätzlich nach `/config/packages/` kopiert werden.

## Neue Helfer

```text
input_number.se_nf_early_open_deficit_kwh
input_number.se_nf_lifetime_min_target_soc_pct
input_number.se_nf_lifetime_max_target_soc_pct
input_text.se_nf_live_consumption_power_entities
sensor.se_nf_live_consumption_power_now
```

## Wichtig nach Update

```bash
ha core check
ha core restart
```

Danach prüfen:

```text
sensor.se_nf_config_check = ok
sensor.se_nf_sanity_check = ok
```

## Mapping neu prüfen

Besonders:

```text
input_text.se_nf_live_consumption_power_entities
input_text.se_nf_live_pv_power_entities
input_text.se_nf_forecast_now_entity
input_text.se_nf_weather_entity
```
