# Portierung auf eine fremde Home-Assistant-Instanz

Dieses Release ist bewusst so dokumentiert, dass es nicht von einer einzelnen privaten Instanz ausgeht.

Trotzdem muss jede Zielinstallation ihre lokalen Entities prüfen und mappen.

## Pflicht: SolarEdge-Entities

Das Package benötigt SolarEdge-Entities für:

```text
number.solaredge_i1_storage_charge_limit
number.solaredge_i1_backup_reserve
sensor.solaredge_i1_b1_state_of_energy
```

Diese Defaults können je nach Installation anders heißen.

## Konfigurierbare SolarEdge-Mappings

```text
input_text.se_nf_charge_limit_entity
input_text.se_nf_battery_soe_entity
input_text.se_nf_backup_reserve_entity
```

## Konfigurierbare lokale Mappings

```text
input_text.se_nf_live_pv_power_entities
input_text.se_nf_live_consumption_power_entities
input_text.se_nf_forecast_now_entity
input_text.se_nf_weather_entity
input_text.se_nf_pv_today_remaining_entity
input_text.se_nf_pv_today_total_entity
input_text.se_nf_pv_tomorrow_entity
input_text.se_nf_pv_overmorrow_entities
input_text.se_nf_daily_consumption_entity
input_text.se_nf_sql_db_path
```

## Wichtige Portierungsstellen

### PV-Ist-Leistung

Default:

```text
sensor.power_solar_generation,sensor.power_solar_generation_filtered,sensor.solaredge_i1_ac_power
```

Auf einer fremden Instanz muss hier der lokale PV-Leistungssensor in Watt eingetragen werden.

### Verbrauchsleistung

Default:

```text
sensor.power_consumption
```

Auf einer fremden Instanz muss hier der Hausverbrauchs-Leistungssensor in Watt eingetragen werden.

### Wetter

Default:

```text
weather.ps8
```

Auf einer fremden Instanz z. B.:

```text
weather.home
weather.forecast_home
```

### PV-Prognose

Default-Beispiele:

```text
sensor.pv_prognose_leistung_jetzt_biased_interpoliert
sensor.pv_prognose_heute_verbleibend_biased
sensor.pv_prognose_heute_06_24_biased
sensor.pv_prognose_morgen_biased
```

Andere Nutzer müssen diese Sensoren auf ihre Forecast-Integration anpassen.

## Nicht blind aktivieren

Auf einer fremden Instanz zuerst:

```text
input_boolean.se_netzdienlich_enabled = off
```

lassen, dann Mapping und Audit ausführen.
