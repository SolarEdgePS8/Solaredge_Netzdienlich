# SolarEdge Netzdienlich Package v2.9.7

Patch-Release für die GitHub Issues #4 und #5 sowie das neue offizielle Dashboard.

## Issue #4 – optionale Mappings

- Tages-PV-Ertrag in Energieeinheiten dokumentiert und validiert.
- Automatischer Fallback auf den internen PV-Tageszähler.
- Tagesverbrauch eindeutig als kumulierter Wert seit Mitternacht erklärt.
- PV-Gesamtzähler wird nach kWh normalisiert.
- EVCC-Rückkanal bleibt bei externer Read-only-Anbindung sicher optional.
- Leere optionale Site-Werte können alte Mappings entfernen.

## Issue #5 – Zeitfenster beim Moduswechsel

- Ladefenster nur gültig bei `Start < Ende`.
- Moduswechsel plant außerhalb einer laufenden Session kontrolliert neu.
- Nachlauf gilt nur für bereits geöffnete Sessions.
- Invertierte Zeitfenster werden verhindert.
- Zusätzliche Diagnoseattribute für Kandidat, aktiven Start, Ende und Session.

## Dashboard

Das portable Lovelace-Dashboard liegt jetzt im Ordner `dashboard/` und verwendet ausschließlich Home-Assistant-Standardkarten.

## Update

Bestehende lokale Helper-Werte bleiben bei einem normalen Update erhalten. `apply_site_config.sh` ist nur erneut notwendig, wenn Mappings oder Startwerte bewusst geändert bzw. optionale Mappings geleert werden sollen.

## Prüfung

- Home-Assistant Config Check: PASS
- Sanity Check: PASS
- Issue-#4-Runtime-Test: PASS
- Issue-#5-Moduswechsel und Zeitreihenfolge: PASS
- Statische YAML-/Manifest-/Hash-Prüfung: PASS
