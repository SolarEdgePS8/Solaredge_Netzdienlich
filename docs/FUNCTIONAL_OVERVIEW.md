# Functional Overview

## Hauptfunktionen

Das Package berechnet ein Ladefenster für den SolarEdge-Speicher.

Es kombiniert:

- Akku-SoE
- Backup-Reserve
- Ziel-SoC
- verfügbare PV-Prognose
- Restverbrauchsprognose
- Live-PV-Leistung
- Live-Verbrauchsleistung
- Wetterbewertung
- Akku-Schonen-Modus
- Sicherheits- und Writer-Logik

## Wichtige Ergebnis-Sensoren

```text
sensor.se_nf_today_charge_window
sensor.se_nf_tomorrow_charge_window
sensor.se_nf_decision_reason
sensor.se_nf_charge_limit_target
sensor.se_nf_charge_limit_actual
sensor.se_nf_desired_target
sensor.se_nf_writer_mode
sensor.se_nf_available_pv_for_battery_today
sensor.se_nf_coverage_ratio
sensor.se_nf_weather_planning_factor_today
sensor.se_nf_weather_lead_minutes
```

## Wetterlogik

Wetter wirkt auf:

- PV-Puffer
- finalen Wetterfaktor
- Weather Lead Minutes
- geplante Startzeit, wenn Wetter schlecht genug ist

Bei gutem Wetter kann `sensor.se_nf_weather_lead_minutes = 0` korrekt sein.

## Akku-Schonen-Modus

Im Modus `Akku schonen` werden eigene Grenzen genutzt:

```text
input_number.se_nf_lifetime_min_soc_pct
input_number.se_nf_lifetime_max_soc_pct
input_number.se_nf_lifetime_min_target_soc_pct
input_number.se_nf_lifetime_max_target_soc_pct
input_number.se_nf_lifetime_start_safety_buffer_min
input_number.se_nf_lifetime_latest_finish_hour
```

## Early-Guard

Die Early-Open-/Critical-Deficit-Logik nutzt in v2.9.5 keine harten lokalen Power-Sensoren mehr, sondern interne Resolver:

```text
sensor.se_nf_live_pv_actual_now
sensor.se_nf_live_consumption_power_now
```
