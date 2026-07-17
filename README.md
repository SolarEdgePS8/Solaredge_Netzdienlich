# SolarEdge Netzdienlich Package v2.9.8

Home-Assistant-Package zur planbaren und netzdienlichen Steuerung eines SolarEdge-Speichers.

Dieses Repository ist ein **Home-Assistant-Package-Bundle**. Es ist keine HACS-Integration. Vor der Aktivierung müssen die Entity-Zuordnungen der jeweiligen Home-Assistant-Instanz eingerichtet und geprüft werden.

## Die zwei wichtigsten Anleitungen

- **Neue Installation:** [`docs/01_FIRST_INSTALL.md`](docs/01_FIRST_INSTALL.md)
- **Update einer bestehenden Installation:** [`docs/02_UPDATE_EXISTING.md`](docs/02_UPDATE_EXISTING.md)

## Struktur

```text
package/      fünf Home-Assistant-Package-Dateien
config/       Vorlage für die einmalige Konfiguration einer neuen Instanz
scripts/      Installation, Runtime-Helfer, Konfiguration, Discovery und Checks
audit/        Read-only-, Manifest- und optionaler Safe-A/B-Test
dashboard/    portables Lovelace-Dashboard und Installationshinweise
docs/         sechs fortlaufend nummerierte Anleitungen
validation/   anonymisierte Release-Gates, Datenschutzhinweis und Datei-Hashes
github/       Release-Text und Veröffentlichungscheckliste
```

## Neue Home-Assistant-Instanz

Kurzablauf:

1. Repository klonen oder ZIP entpacken.
2. `scripts/install_package.sh` ausführen.
3. Home Assistant prüfen und neu starten.
4. `config/site_config.env.example` nach `config/site_config.env` kopieren.
5. Eigene Entity-IDs und Parameter eintragen.
6. `SITE_CONFIG_CONFIRMED=YES` setzen.
7. `scripts/apply_site_config.sh` ausführen.
8. Read-only-Audit ausführen.
9. Master-Schalter erst danach aktivieren.

## Dynamischer Modus „Akku schonen“ in v2.9.8

v2.9.8 ermittelt Nacht- und Tagesverbrauch aus zwei lückenlos verbundenen,
dynamischen 7-Tage-Fenstern. Die gemeinsame Grenze folgt dem Sonnenaufgang
plus einem einstellbaren PV-Bereitschaftsversatz. Der Median ist robust gegen
einzelne Ausreißertage.

Das Ziel berücksichtigt Backup-Reserve, gepufferten Tag-/Nachtbedarf,
Sicherheitsenergie sowie die verfügbaren PV-Prognosen für morgen und – sofern
vorhanden – übermorgen. `sensor.se_nf_effective_target_soc_pct` ist die
kanonische Zielquelle; `sensor.speicher_ziel_ladestand` bleibt ein identischer
Kompatibilitätsalias.

Ohne Backup-System bleibt `input_text.se_nf_backup_reserve_entity` leer. Dann
verwendet das Package `input_number.se_nf_backup_reserve_fallback_pct`,
standardmäßig `0 %`.

## Optionale Mappings

- `ACTUAL_PV_TODAY_ENTITIES`: heutiger PV-Ertrag in `Wh`, `kWh` oder `MWh`.
- `DAILY_CONSUMPTION_ENTITY`: heutiger kumulierter Hausverbrauch, kein Durchschnitt.
- `PV_ACTUAL_METER_SOURCE_ENTITY`: fortlaufender PV-Gesamtenergiezähler.
- `EVCC_BATTERY_MODE_ENTITY`: optionaler Rückkanal von evcc zu Home Assistant.

Ist kein direkter Tagesertragssensor vorhanden, kann das Package den intern erzeugten
`sensor.se_nf_pv_actual_today_meter` automatisch als Fallback verwenden.

## Ladefenster und Moduswechsel

v2.9.8 prüft strikt, dass ein aktiver Start vor dem aktuellen Fensterende liegt. Beim bewussten Wechsel zwischen `Akku schonen` und `Netzdienlich laden` wird außerhalb einer laufenden Session neu geplant. Eine aktive Session wird nicht rückwirkend verschoben.

Das Dashboard unter [`dashboard/`](dashboard/) zeigt Kandidat, gespeicherten Start, aktiven Start, Fensterende und Session-Zustand gemeinsam an.

## PV-Ist-Leistung einfach erklärt

Der Helfer `input_text.se_nf_live_pv_power_entities` erwartet mindestens einen Sensor für die **aktuelle PV-Leistung in Watt**. Mehrere Einträge sind als kommaseparierte Fallback-Liste möglich. `_filtered` ist keine Pflicht; Energiezähler in `kWh` sind hier falsch.

## Sicherheit

Der Master-Schalter bleibt bei einer neuen Installation zunächst aus. Vor der Aktivierung müssen mindestens gelten:

```text
sensor.se_nf_config_check = ok
sensor.se_nf_sanity_check = ok
```

`writer_mode = normal` kann ein gültiger Ruhezustand sein. Entscheidend sind plausible Ziel-/Istwerte und grüne Config-/Sanity-Checks.

## Release-Gates

```text
GATE_STATIC_MAIN_CRITICAL: PASS
critical_main: 0
GATE_RUNTIME: PASS
runtime_fail_count: 0
GATE_MANIFEST: PASS_OR_EXTERNAL_REVIEW
critical_internal: 0
```
