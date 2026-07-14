# SolarEdge Netzdienlich Package v2.9.6

Home-Assistant-Package zur planbaren und netzdienlichen Steuerung eines SolarEdge-Speichers.

Dieses Repository ist ein **Home-Assistant-Package-Bundle**. Es ist keine HACS-Integration. Vor der Aktivierung müssen die Entity-Zuordnungen der jeweiligen Home-Assistant-Instanz eingerichtet und geprüft werden.

## Die zwei wichtigsten Anleitungen

- **Neue Installation:** [`docs/01_FIRST_INSTALL.md`](docs/01_FIRST_INSTALL.md)
- **Update einer bestehenden Installation:** [`docs/02_UPDATE_EXISTING.md`](docs/02_UPDATE_EXISTING.md)

Damit gibt es nicht mehr mehrere konkurrierende Installationsanleitungen.

## Struktur

```text
package/      vier Home-Assistant-Package-Dateien
config/       Vorlage für die einmalige Konfiguration einer neuen Instanz
scripts/      Installation, Konfiguration, Discovery und erster Check
audit/        Read-only-, Manifest- und optionaler Safe-A/B-Test
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

## Warum ist eine Site-Konfiguration nötig?

Entity-Namen unterscheiden sich zwischen Home-Assistant-Instanzen. Das Package darf nicht an Namen wie `sensor.power_solar_generation` oder `weather.ps8` gebunden sein. Die lokale Instanz teilt dem Package deshalb über `input_text.se_nf_*` mit, welche Sensoren es verwenden soll.

## PV-Ist-Leistung einfach erklärt

Der Helfer lautet:

```text
input_text.se_nf_live_pv_power_entities
```

Hier gehört mindestens ein Sensor für die **aktuelle PV-Leistung in Watt** hinein.

Beispiel:

```text
sensor.meine_pv_leistung
```

Mehrere Einträge sind als Fallback-Liste möglich:

```text
sensor.meine_pv_leistung,sensor.meine_pv_leistung_gefiltert,sensor.mein_wechselrichter_ac_power
```

`_filtered` ist keine Pflicht. Es bezeichnet lediglich einen optional geglätteten Sensor. Das Package nimmt den ersten gültigen Sensor der Liste. Energiezähler in `kWh` sind an dieser Stelle falsch.

## Sicherheit

Der Master-Schalter bleibt bei einer neuen Installation zunächst aus:

```text
input_boolean.se_netzdienlich_enabled = off
```

Vor der Aktivierung müssen mindestens gelten:

```text
sensor.se_nf_config_check = ok
sensor.se_nf_sanity_check = ok
```

`writer_mode = normal` kann ebenfalls ein gültiger Ruhezustand sein. Entscheidend sind plausible Ziel-/Istwerte und grüne Config-/Sanity-Checks.

## Release-Gates

```text
GATE_STATIC_MAIN_CRITICAL: PASS
critical_main: 0
GATE_RUNTIME: PASS
runtime_fail_count: 0
GATE_MANIFEST: PASS_OR_EXTERNAL_REVIEW
critical_internal: 0
```
