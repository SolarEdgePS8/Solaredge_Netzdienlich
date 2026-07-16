# Runtime-Test GitHub Issues #4 und #5

Testdatum: 2026-07-16  
Quelle: lokale Home-Assistant-Testinstallation, anonymisierte Terminalausgabe

## Issue #4

```text
config_check = ok
sanity_check = ok
pv_source = sensor.se_nf_pv_actual_today_meter
pv_actual_kwh = 38.9
evcc_request = off
evcc_mapping_status = optional_inactive
critical_failures = []
```

Ergebnis: automatischer PV-Tageszähler-Fallback aktiv; externer evcc-Betrieb ohne Rückkanal bleibt sicher inaktiv.

## Issue #5

Nach Wechsel von `Akku schonen` zu `Netzdienlich laden` außerhalb einer aktiven Session:

```text
candidate_start = 11:45
stored_start = 11:45
active_start = 11:45
window_end = 14:15
window = 11:45–14:15
session_state = done
```

Der Test fand nach dem neuen Fensterende statt; `done` war deshalb korrekt. Kandidat, persistenter Helper und aktiver Start stimmen überein. Die Zeitreihenfolge ist gültig und das zuvor reproduzierte invertierte Fenster tritt nicht mehr auf.
