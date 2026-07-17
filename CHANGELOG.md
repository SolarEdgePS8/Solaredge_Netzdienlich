# Changelog

## v2.9.8

### Dynamisches und resilientes Akku-schonen-Ziel

- Nacht- und Tagesverbrauch werden aus zwei lückenlos verbundenen dynamischen
  7-Tage-Fenstern als Median ermittelt.
- Die gemeinsame Grenze folgt Sonnenaufgang plus konfigurierbarem
  PV-Bereitschaftsversatz.
- Das Ziel berücksichtigt Backup-Reserve, gepufferten Tag-/Nachtbedarf,
  Sicherheitsenergie und verfügbare PV-Prognosen bis zu 48 Stunden.
- `sensor.se_nf_effective_target_soc_pct` ist die kanonische Zielquelle;
  `sensor.speicher_ziel_ladestand` bleibt ein identischer Alias.
- Dashboard-Kopf und Ziel-Gauge zeigen den aktiven Zielwert statt immer den
  festen netzdienlichen Einstellwert.

### GitHub Issues #5 und #6

- Moduswechsel planen außerhalb einer laufenden Session Ziel und Startzeit
  konsistent neu; alle drei Modi wurden in einer vollständigen Live-Abnahme
  geprüft.
- Der von der Konfiguration referenzierte
  `se_nf_load_forecast_7d_cached.py` sowie die neuen Tag-/Nacht-Helfer werden
  jetzt mit ausgeliefert und vom Installer nach `/config` kopiert.

### Portabilität und Installation

- Backup-Reserve ist für Anlagen ohne Backup-System optional und besitzt einen
  konfigurierbaren Fallback.
- Die Critical-Deficit-Logik nutzt kanonische, gemappte SoE-/Reserve-Sensoren.
- Doppelte Refresh-Sidecars wurden zu einer Automation zusammengeführt.
- Eine globale Unterdrückung fremder Home-Assistant-Logs ist nicht Teil des
  Releases.
- Der ungenutzte parallele Min-/Max-Zielpfad aus
  `se_nf_09_lifetime_target_helpers.yaml` wird beim Update gesichert und
  deaktiviert.
- Installer, Manifeste, Audit-Suite und Dokumentation enthalten alle fünf
  Packages und drei Runtime-Helfer.
- Der ausführende Modustester akzeptiert den beabsichtigten `5000 W`-
  Fail-open-Zustand bei ausgeschaltetem Master und isoliert die physischen
  Writer vor jeder Testumschaltung.

## v2.9.7

### GitHub Issue #4 – optionale Mappings

- `ACTUAL_PV_TODAY_ENTITIES` als Tagesenergie in `Wh`, `kWh` oder `MWh` dokumentiert und validiert.
- Automatischer Fallback auf `sensor.se_nf_pv_actual_today_meter`, wenn ein gültiger PV-Gesamtzähler konfiguriert ist.
- `DAILY_CONSUMPTION_ENTITY` eindeutig als kumulierter Tagesverbrauch erklärt; der Durchschnitt wird intern aus der Historie berechnet.
- `PV_ACTUAL_METER_SOURCE_ENTITY` normalisiert `Wh` und `MWh` nach `kWh`.
- `EVCC_BATTERY_MODE_ENTITY` bleibt bei leerem, unbekanntem oder nicht vorhandenen Rückkanal sicher inaktiv und liefert Diagnoseattribute.
- Leere optionale Werte in `site_config.env` können vorhandene alte Helper-Mappings entfernen.
- First-Run-Check um optionale Mapping-Diagnosen erweitert.

### GitHub Issue #5 – Ladefenster beim Moduswechsel

- Strikte Gültigkeitsregel `Start < Ende` für das aktive Tagesfenster.
- Gespeicherte Startwerte nach einem Moduswechsel werden nur weiterverwendet, wenn sie zum neuen Fenster passen.
- Bewusster Moduswechsel kann außerhalb einer aktiven Session die normale Replan-Schwelle einmalig umgehen.
- Nachlaufzeit verlängert nur eine bereits geöffnete Session und legitimiert keinen neuen Start nach dem regulären Fensterende.
- Invertierte Anzeigen wie `14:45–14:15` werden verhindert.
- Zeitfenster-Sensor erhält Diagnoseattribute für Start, Ende, Quelle und Session-Zustand.

### Dashboard und Audit

- Offizielles Lovelace-Dashboard als Bestandteil des Release-Bundles aufgenommen.
- Audit-Installationspfad auf den versionsneutralen Pfad `/share/se_nf_release_audit` umgestellt.
- Release-Validierung und Datei-Hashes für v2.9.7 neu erzeugt.

## v2.9.6

### YAML-Robustheit

- Sensoralter nutzt bevorzugt `last_reported` und fällt auf `last_updated` zurück.
- Behebt mögliche `battery_soe_stale`-Fehlalarme bei regelmäßig gemeldeten, aber unveränderten Sensorwerten.
- SolarEdge-Writer verbucht `last_write`, Write-Lock und `last_applied` erst nach erfolgreichem `number.set_value`.
- Harter `number.solaredge_i1_storage_charge_limit`-Trigger aus dem Haupt-Writer entfernt.
- Writer-Safety-Sidecar nutzt das konfigurierte Charge-Limit-Mapping.
- Optionales `input_text.se_nf_discharge_limit_entity` ergänzt.
- Hartes Hausverbrauchs-`initial` aus dem Planning-Helper entfernt, damit lokale Mappings Neustarts überleben.
- Fallback-Resolver akzeptieren einen gültigen ersten Wert von `0 W` und wechseln danach nicht zu einem späteren Kandidaten.
- Master-AUS-Defaults schreiben nur noch bei echter Abweichung und verhindern überlappende Läufe.

### Erstinstallation und Portierung

- Eine eindeutige Erstinstallationsanleitung.
- Eine separate Update-Anleitung.
- Site-Konfigurationsvorlage mit Pflicht-Mappings und einmaligen Startwerten.
- Discovery-Script für Power-, Energy-, Weather-, SoE- und SolarEdge-Kandidaten.
- `apply_site_config.sh` setzt Mappings, ohne den Master zu aktivieren.
- Erklärung von `_filtered`, `entity` und `entities`.
- Klare Unterscheidung zwischen Leistung in `W` und Energie in `kWh`.

### Repository-Aufräumen

- Doppelte First-Run-Skripte entfernt.
- Nur noch `scripts/run_first_checks.sh`.
- Audit-Python-Dateien verständlich dokumentiert.
- Dokumentation fortlaufend nummeriert.
- Backup-Dateien und alte Audit-Baks nicht im Release enthalten.

### GitHub Issues berücksichtigt

- Issue #1: Fresh-install Defaults, `battery_soe_stale`, gültiger `writer_mode=normal`.
- Issue #2: Modbus-Fehler und Writer-Bookkeeping nach erfolgreichem Write.
- Issue #3: PV-Mapping, `_filtered` und Fallback-Listen.
