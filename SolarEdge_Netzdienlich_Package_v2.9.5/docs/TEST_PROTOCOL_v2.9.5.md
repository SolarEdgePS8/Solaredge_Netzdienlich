# Testprotokoll v2.9.5

## Weather-A/B

Geprüft:

```text
Wetter AUS -> final 1.0, Weather Lead 0
Wetter EIN -> echter Wetterfaktor
Wettergewicht verändert finalen Faktor
PV-Puffer reagiert auf Wetter
Startzeit verschiebt sich nur bei schlechterem Wetterfaktor
```

## Modus-Startpuffer

Fix:

```jinja
{% set buffer = states('sensor.se_nf_mode_start_safety_buffer_min') | int(30) %}
```

statt direktem Zugriff auf den normalen Startpuffer.

Geprüft im Modus `Akku schonen`:

```text
Lifetime Buffer 0 min   -> Start später
Lifetime Buffer 120 min -> Start deutlich früher
```

## Forecast-Fallback

Alte restored Abhängigkeit entfernt:

```text
sensor.se_nf_forecast_pv_now
```

Neue aktive Quellen:

```text
sensor.pv_prognose_leistung_jetzt_biased_interpoliert
sensor.evcc_forecast_solar
```

## Early-Guard Legacy-Fix

Entfernt:

```text
sensor.se_nf_good_day_for_late_start
sensor.se_nf_effective_available_pv_for_battery
sensor.se_nf_effective_pv_delta
```

Neue Berechnung:

```jinja
effective_pv = sensor.se_nf_available_pv_for_battery_today
delta = effective_pv - need
good_day = coverage >= 1.2 and pv_for_akku >= need
```

## Portability-Fix Power-Sensoren

Vorher hart:

```text
sensor.power_solar_generation
sensor.power_consumption
```

Jetzt intern:

```text
sensor.se_nf_live_pv_actual_now
sensor.se_nf_live_consumption_power_now
```

## Release-Gates

```text
GATE_STATIC_MAIN_CRITICAL: PASS
critical_main: 0
GATE_RUNTIME: PASS
runtime_fail_count: 0
GATE_MANIFEST: PASS_OR_EXTERNAL_REVIEW
critical_internal: 0
```
