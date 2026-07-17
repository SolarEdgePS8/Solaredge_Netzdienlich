# 03 – Entity-Mapping verständlich erklärt

## Warum Mappings?

Jede Home-Assistant-Instanz verwendet andere Entity-IDs. Das Package nutzt deshalb Mapping-Helfer. Dort wird eingetragen, welcher lokale Sensor welche Aufgabe erfüllt.

## Pflicht-Mappings

| Zweck | Mapping-Helfer | Erwartete Einheit |
|---|---|---|
| SolarEdge Charge-Limit | `input_text.se_nf_charge_limit_entity` | `W`, beschreibbare `number` |
| Akku-SoE | `input_text.se_nf_battery_soe_entity` | `%` |
| Akkukapazität | `input_text.se_nf_battery_capacity_entity` | `kWh` |
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


<!-- ISSUE-4-OPTIONAL-MAPPINGS-START -->
## Optionale Mappings

### `BACKUP_RESERVE_ENTITY`

Optionaler, dynamisch einstellbarer Backup-Reserve-Sensor in Prozent, zum
Beispiel eine beschreibbare `number` der SolarEdge-Integration. Anlagen ohne
Backup-System lassen das Mapping leer. In diesem Fall verwendet das Package
`input_number.se_nf_backup_reserve_fallback_pct`; der empfohlene Ausgangswert
ohne reservierte Backup-Kapazität ist `0 %`.

### `ACTUAL_PV_TODAY_ENTITIES`

Ein Sensor oder eine kommaseparierte Fallback-Liste für den **seit Mitternacht
erzeugten PV-Ertrag**. Erwartet wird Energie in `Wh`, `kWh` oder `MWh`, keine
Momentanleistung in Watt. Das Package verwendet den ersten numerischen und
verfügbaren Energiesensor.

Ist kein gültiger Tagesertragssensor vorhanden, aber
`PV_ACTUAL_METER_SOURCE_ENTITY` zeigt auf einen gültigen fortlaufenden
PV-Gesamtzähler, verwendet das Package automatisch
`sensor.se_nf_pv_actual_today_meter`.

### `DAILY_CONSUMPTION_ENTITY`

Hier ist **kein Durchschnitt** gefragt. Eingetragen wird der seit Mitternacht
kumulierte Hausverbrauch in `kWh`. Aus der Recorder-Historie berechnet das
Package selbst das 7-Tage-Verbrauchsprofil. Ohne gültiges Mapping oder ohne
ausreichende Historie greift der manuelle Tagesverbrauchs-Fallback.

### `PV_ACTUAL_METER_SOURCE_ENTITY`

Fortlaufender PV-Gesamtenergiezähler in `Wh`, `kWh` oder `MWh`, normalerweise
mit `state_class: total` oder `total_increasing`. Das Package normalisiert die
Quelle nach `kWh` und erzeugt daraus den täglich zurückgesetzten
`sensor.se_nf_pv_actual_today_meter`.

### `EVCC_BATTERY_MODE_ENTITY`

Optionaler Rückkanal von evcc zu Home Assistant. Zustände wie `charge`,
`grid_charge` oder `laden` können den EVCC-Override aktivieren. Zustände wie
`discharge`, `entladen`, `hold`, `normal`, `unknown`, `unbekannt` oder ein leeres
Mapping lösen keine Ladeanforderung aus.

Läuft evcc extern und liest ausschließlich Werte aus Home Assistant, bleibt das
Mapping leer.

Ab v2.9.8 schreiben leere Werte
in `site_config.env` auch das optionale Backup-Mapping und die übrigen
optionalen Helper tatsächlich leer. Dadurch lassen
sich alte optionale Mappings entfernen.
<!-- ISSUE-4-OPTIONAL-MAPPINGS-END -->

## Mappings werden nicht in der YAML umbenannt

Die eigenen Sensoren werden in `config/site_config.env` eingetragen und anschließend mit `scripts/apply_site_config.sh` auf die `input_text.se_nf_*`-Helfer übertragen.
