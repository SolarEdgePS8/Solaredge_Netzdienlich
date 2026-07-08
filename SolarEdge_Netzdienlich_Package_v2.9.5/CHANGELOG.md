# Changelog

## v2.9.5

### Fixes

- Wetter-Final-Faktor wirkt jetzt auf Weather Lead Minutes.
- Wettergewicht beeinflusst dadurch wieder sichtbar die geplante Startzeit.
- Wetterplanung EIN/AUS verschiebt Faktor, PV-Puffer und Startlogik korrekt.
- Start-Sicherheitspuffer nutzt jetzt den modusabhängigen Sensor.
- Im Modus Akku schonen wirkt der Akku-schonen-Zeitpuffer korrekt auf Candidate, Active und Planned Start.
- PV-Forecast-Fallback von altem restored Sensor auf aktive Forecast-Quellen umgestellt.
- Critical-Deficit-/Early-Open-Guard von alten unavailable Effective-PV-Sensoren entkoppelt.
- Delta-Berechnung im Critical-Deficit-Guard nutzt jetzt aktuelle PV-Pufferlogik.
- Early-Open-Defizit-Helfer als Package-Helfer wiederhergestellt.
- Lifetime-Min-/Max-Target-SoC-Helfer ergänzt.
- Live-Verbrauchsleistung über `input_text.se_nf_live_consumption_power_entities` konfigurierbar gemacht.
- Early-Guard nutzt jetzt interne Resolver statt harter lokaler Power-Sensoren.

### Validation

- Dependency-Audit: kritische Hauptpaket-Abhängigkeiten auf 0 reduziert.
- Manifest-Audit: `critical_internal: 0`.
- Runtime-Audit: `runtime_fail_count: 0`.
- Wetter-A/B-Test geprüft.
- Adaptive-Forecast-Kette geprüft: Bias und Summary liefern gültige Werte.
- Read-only-, Runtime-, Manifest-, Portability- und Safe-A/B-Release-Audits ergänzt.

### Integration

- Release-Audit-Suite integriert.
- Portability-Audit erkennt harte lokale Entity-Abhängigkeiten, fehlende Helfer, restored Legacy-Sensoren und kritische Hauptpaket-Abhängigkeiten.
- Verbrauchsleistung ist nun über Input-Text-Helfer konfigurierbar.
