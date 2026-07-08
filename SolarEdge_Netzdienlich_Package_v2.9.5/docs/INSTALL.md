# Installation

## Voraussetzungen

- Home Assistant mit aktivierten Packages
- SolarEdge-Integration mit Speicher-Entities
- Terminal-/SSH-Zugriff empfohlen
- Grundverständnis von Home-Assistant-Entities

## Package-Support aktivieren

In `/config/configuration.yaml`:

```yaml
homeassistant:
  packages: !include_dir_named packages
```

Danach Home Assistant neu starten.

## Dateien kopieren

Aus diesem Release:

```text
package/solaredge_netzdienlich.yaml
package/se_nf_07_writer_safety.yaml
package/se_nf_08_planning_helpers.yaml
package/se_nf_09_lifetime_target_helpers.yaml
```

nach:

```text
/config/packages/
```

## YAML prüfen

```bash
ha core check
```

Wenn erfolgreich:

```bash
ha core restart
```

## Master-Schalter

Das Package definiert:

```text
input_boolean.se_netzdienlich_enabled
input_boolean.se_netzdienlich_debug
```

Vor der ersten produktiven Aktivierung sollte `input_boolean.se_netzdienlich_enabled` ausgeschaltet bleiben.

## Pflichtprüfung nach Neustart

```bash
for e in \
sensor.se_nf_config_check \
sensor.se_nf_sanity_check \
sensor.se_nf_writer_mode \
sensor.se_nf_today_charge_window \
sensor.se_nf_decision_reason
do
  echo
  echo "### $e"
  curl -sS -H "Authorization: Bearer $SUPERVISOR_TOKEN" \
    "http://supervisor/core/api/states/$e"
done
```
