# 05 – Troubleshooting

## `battery_soe_stale`

Dieser Zustand bedeutet, dass das Package den Akku-SoE-Sensor als zu alt bewertet.

v2.9.7 berechnet das Alter bevorzugt aus `last_reported`. Dadurch wird ein regelmäßig gemeldeter, aber unveränderter Akkuwert nicht mehr fälschlich nur wegen `last_updated` als alt angesehen.

Prüfen:

```text
input_text.se_nf_battery_soe_entity
sensor.se_nf_soe_age_s
input_number.se_nf_max_sensor_age_s
```

Für neue Installationen setzt die Site-Konfigurationsvorlage standardmäßig:

```text
MAX_SENSOR_AGE_S=1800
```

Das sind 30 Minuten. Durch die last_reported-Prüfung bleiben unveränderte, aber regelmäßig gemeldete Werte gültig; eine tatsächlich ausgefallene Verbindung wird weiterhin zeitnah erkannt.

## `writer_mode = normal`

`normal` ist kein Fehler. Es bedeutet, dass der Writer grundsätzlich im normalen Betriebsmodus ist. Entscheidend sind:

```text
sensor.se_nf_config_check = ok
sensor.se_nf_sanity_check = ok
```

sowie plausible Werte für Target, Desired und Actual.

## `Deaktiviert · Ladebegrenzung freigegeben (Fail-open)`

Bei ausgeschaltetem Master kann dies ein erwarteter Zustand sein. Das Package soll bei deaktivierter Steuerung keine künstliche Ladebegrenzung zurücklassen.

## Modbus: `No response received after 3 retries`

Das ist zunächst ein Kommunikationsfehler zwischen Home Assistant und Wechselrichter bzw. Modbus-Proxy.

Prüfen:

- Wechselrichter erreichbar?
- Modbus TCP aktiv?
- korrekte Unit-/Inverter-ID?
- nur ein Modbus-Client bzw. sauberer Proxy?
- parallele Schreibautomationen deaktiviert?
- SolarEdge-Integration aktuell und stabil?

v2.9.7 behebt zusätzlich einen internen Robustheitspunkt: `last_write`, Write-Lock und `last_applied` werden erst nach einem erfolgreichen `number.set_value` aktualisiert. Schlägt der Modbus-Service fehl, wird der Write also nicht mehr fälschlich als erfolgreich verbucht.

Es werden bewusst keine zusätzlichen aggressiven Schreibwiederholungen eingebaut, weil die Integration selbst bereits Wiederholungen ausführt und weitere Retries den Modbus-Verkehr verschärfen könnten.

## Startzeit oder Forecast wirkt unplausibel

Zuerst die Einheiten prüfen:

- Live-Leistung: `W`
- Energieprognosen: `kWh`
- SoE/Reserve: `%`

Danach Read-only-Audit und Mapping-Check ausführen.

## Zeitfenster ändert sich beim Moduswechsel nicht

Prüfen:

```text
input_select.se_nf_optimization_mode
sensor.se_nf_optimization_mode_effective
sensor.se_nf_today_planned_start_candidate_timestamp
input_datetime.se_nf_session_planned_start
sensor.se_nf_active_planned_start_timestamp
sensor.se_nf_today_end_timestamp
input_select.se_nf_session_state
```

Bei einer bereits geöffneten Session darf der historische Start stabil bleiben. Außerhalb einer aktiven Session müssen der neue Kandidat und der aktive Plan jedoch zusammenpassen. Ein Fenster mit `Start >= Ende` ist immer ungültig und wird ab v2.9.7 nicht mehr als normales Ladefenster ausgegeben.
