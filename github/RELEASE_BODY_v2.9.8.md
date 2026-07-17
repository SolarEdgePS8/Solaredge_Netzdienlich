# SolarEdge Netzdienlich Package v2.9.8

Release mit dynamischem Akku-schonen-Ziel, vollständigem Runtime-Paket und
Korrekturen für die GitHub Issues #5 und #6.

## Dynamisches Akku-schonen-Ziel

- Nacht- und Tagesverbrauch aus zwei lückenlos verbundenen dynamischen
  7-Tage-Fenstern.
- Robuster Median statt eines starren oder kumulativ aufgeblähten Nachtwerts.
- Gemeinsame Grenze aus Sonnenaufgang plus einstellbarem
  PV-Bereitschaftsversatz.
- Resilientes Ziel aus Backup-Reserve, gepuffertem Tag-/Nachtbedarf,
  Sicherheitsenergie sowie PV-Prognosen für morgen und optional übermorgen.
- Ein kanonischer Zielpfad; `sensor.speicher_ziel_ladestand` ist nur noch
  Kompatibilitätsalias.
- Dashboard-Kopf und Ziel-Gauge zeigen in jedem Modus denselben aktiven
  Zielwert.

## Issue #5 – Moduswechsel und Zielpfad

- Gespeicherter und aktiver Start werden außerhalb einer laufenden Session an
  den neu gewählten Modus angepasst.
- Start und Ende müssen eine gültige Reihenfolge besitzen.
- Ziel, Energiebedarf und Ladezeit verwenden dieselbe kanonische Zielquelle.

## Issue #6 – fehlende Python-Dateien

Der Installer liefert jetzt alle drei zur Laufzeit benötigten Helfer aus:

- `se_nf_load_forecast_7d_cached.py`
- `se_nf_night_forecast_7d.py`
- `se_nf_daytime_forecast_7d.py`

## Portabilität und Sicherheit

- Backup-Mapping ist für Anlagen ohne Backup-System optional; dafür existiert
  ein einstellbarer Fallback.
- Critical-Deficit nutzt die kanonisch gemappten SoE-/Reserve-Sensoren.
- Das ungenutzte Parallel-Ziel-Sidecar `se_nf_09_lifetime_target_helpers.yaml`
  wird beim Update gesichert und deaktiviert; es bleibt nur ein Min-/Max-Pfad.
- Nur eine Refresh-Automation für Tag- und Nachthistorie.
- Keine globale Unterdrückung fremder Home-Assistant-Logs.
- Installer sichert ersetzte oder deaktivierte Dateien unter `/share`.
- Der Modustester akzeptiert den beabsichtigten Fail-open-Zustand bei
  ausgeschaltetem Master und isoliert Writer vor der ersten Umschaltung.

## Verifikation

- Home-Assistant Config Check auf der Referenzinstanz: PASS
- Vollständiger Moduswechseltest: 79/79 PASS, Cleanup erfolgreich
- Resilienz- und Szenarientest: 29/29 PASS
- Python-Kompilierung, YAML-Prüfung, Manifest- und Datenschutzprüfung: PASS

Vor der Aktivierung müssen auf jeder Installation
`sensor.se_nf_config_check` und `sensor.se_nf_sanity_check` den Zustand `ok`
melden.
