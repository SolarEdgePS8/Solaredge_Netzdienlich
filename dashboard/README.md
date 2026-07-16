# Dashboard für SolarEdge Netzdienlich

Diese Datei enthält ein portables Home-Assistant-Lovelace-Dashboard für das
SolarEdge-Netzdienlich-Package.

## Dateien

- `solaredge_netzdienlich_dashboard.yaml` – vollständiger `vertical-stack`
- `README.md` – Installation und Hinweise

## Installation

1. In Home Assistant das gewünschte Dashboard öffnen.
2. **Dashboard bearbeiten** auswählen.
3. **Karte hinzufügen** und anschließend **Manuell** auswählen.
4. Den vollständigen Inhalt von
   `solaredge_netzdienlich_dashboard.yaml` einfügen.
5. Speichern.

Die Datei verwendet ausschließlich Home-Assistant-Standardkarten. `card-mod`,
Mushroom oder andere Custom Cards sind nicht erforderlich.

## Zweck

Das Dashboard zeigt:

- aktive Speicherstrategie und Session-Zustand
- Config Check, Sanity Check und Schutzmodus
- Akku-SoE, Energiebedarf und Lade-Limits
- Ladefenster für heute und morgen
- Wetter- und Verbrauchsprognose
- Writer- und Write-Lock-Diagnose
- modusspezifische Planungswerte
- Startkandidat, gespeicherten Start, aktiven Start und Fensterende

## Diagnose eines Moduswechsels

Die Karte **Planungswerte · Diagnose für Moduswechsel** ist für Fälle wie
GitHub Issue #5 vorgesehen.

Beim Wechsel zwischen `Akku schonen` und `Netzdienlich laden` sollten mindestens
diese Werte betrachtet werden:

1. `sensor.se_nf_optimization_mode_effective`
2. `sensor.se_nf_today_planned_start_candidate_timestamp`
3. `input_datetime.se_nf_session_planned_start`
4. `sensor.se_nf_active_planned_start_timestamp`
5. `sensor.se_nf_today_end_timestamp`
6. `input_select.se_nf_session_state`

Das Dashboard markiert ein Zeitfenster als ungültig, wenn der aktive Start nicht
vor dem aktuellen Fensterende liegt.

## Wichtig: Dashboard und Steuerungslogik

Das Dashboard stellt nur Entity-Zustände dar. Es berechnet und schreibt keine
SolarEdge-Werte. Ein veraltetes Dashboard kann den Eindruck erwecken, dass sich
ein Plan nicht ändert, wenn es eine alte oder andere Entity anzeigt.

Wenn jedoch bereits `sensor.se_nf_today_charge_window` selbst einen alten oder
invertierten Wert liefert, liegt die Ursache in der Package-Logik und nicht in
der Darstellung.

## Portabilität

Das Dashboard verwendet nach Möglichkeit nur `se_nf_*`-Entities des Packages.
Für den effektiven Ziel-Ladestand versucht die Kopfkarte zuerst
`sensor.speicher_ziel_ladestand` und fällt andernfalls auf
`input_number.se_nf_target_soc_pct` zurück.

Falls eine optionale Entity in einer Installation nicht existiert, kann die
betreffende Zeile aus der Entities-Karte entfernt werden.

## Empfohlene Repository-Struktur

```text
dashboard/
├── README.md
└── solaredge_netzdienlich_dashboard.yaml
```

Bei späteren Package-Releases sollte die Dashboard-Datei gemeinsam mit der
Package-Version geprüft werden.
