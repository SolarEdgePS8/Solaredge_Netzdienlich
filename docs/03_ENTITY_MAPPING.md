# 03 – Entity-Mapping verständlich erklärt

## Warum Mappings?

Jede Home-Assistant-Instanz verwendet andere Entity-IDs. Das Package nutzt deshalb Mapping-Helfer. Dort wird eingetragen, welcher lokale Sensor welche Aufgabe erfüllt.

## Pflicht-Mappings

| Zweck | Mapping-Helfer | Erwartete Einheit |
|---|---|---|
| SolarEdge Charge-Limit | `input_text.se_nf_charge_limit_entity` | `W`, beschreibbare `number` |
| Akku-SoE | `input_text.se_nf_battery_soe_entity` | `%` |
| Akkukapazität | `input_text.se_nf_battery_capacity_entity` | `kWh` |
| Backup-Reserve | `input_text.se_nf_backup_reserve_entity` | `%` |
| verbleibende PV heute | `input_text.se_nf_pv_today_remaining_entity` | `kWh` |
| PV gesamt heute | `input_text.se_nf_pv_today_total_entity` | `kWh` |
| PV morgen | `input_text.se_nf_pv_tomorrow_entity` | `kWh` |
| aktuelles Wetter | `input_text.se_nf_weather_entity` | `weather.*` |
| Live-PV-Leistung | `input_text.se_nf_live_pv_power_entities` | `W` |
| Live-Hausverbrauch | `input_text.se_nf_live_consumption_power_entities` | `W` |

## Warum endet manches auf `entity` und anderes auf `entities`?

- `..._entity`: genau eine Entity-ID.
- `..._entities`: mehrere mögliche Entity-IDs als kommaseparierte Fallback-Liste.

Beispiel:

```text
sensor.pv_power,sensor.pv_power_filtered,sensor.inverter_ac_power
```

Das Package prüft von links nach rechts und nimmt den ersten aktuell gültigen Wert.

## Was bedeutet `_filtered`?

`_filtered` ist lediglich ein frei gewählter Namenszusatz. Er bedeutet normalerweise, dass der Messwert geglättet wurde.

Beispiel eines ungefilterten Signals:

```text
2100 W → 3400 W → 1800 W → 3600 W
```

Ein Filter kann kurze Sprünge glätten. Ein solcher Sensor ist **optional**. Wer nur einen normalen PV-Leistungssensor besitzt, trägt nur diesen ein.

## Richtig und falsch bei PV-Ist-Leistung

Richtig:

```text
sensor.meine_pv_leistung = 2450 W
```

Falsch:

```text
sensor.pv_ertrag_heute = 18.4 kWh
sensor.pv_energie_gesamt = 12500 kWh
```

Das Package benötigt an dieser Stelle Momentanleistung, keine Energie.

## Mappings werden nicht in der YAML umbenannt

Die eigenen Sensoren werden in `config/site_config.env` eingetragen und anschließend mit `scripts/apply_site_config.sh` auf die `input_text.se_nf_*`-Helfer übertragen.
