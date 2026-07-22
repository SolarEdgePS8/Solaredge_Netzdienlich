# Migration zum SolarEdge HA Energy Controller

Diese Anleitung richtet sich an bestehende Nutzer von `Solaredge_Netzdienlich`.

## Wichtig

Die beiden Projekte dürfen nicht gemischt betrieben werden. Verwende nach der Umstellung nur noch die Dateien des neuen Projekts:

**https://github.com/SolarEdgePS8/SolarEdge_HA_Energy_Controller**

## Empfohlener Ablauf

1. Vollständiges Home-Assistant-Backup erstellen.
2. Aktuelles Release des Nachfolgeprojekts herunterladen.
3. ZIP und SHA256-Datei nach `/share` kopieren.
4. Prüfsumme kontrollieren.
5. Release in einen leeren Ordner entpacken.
6. Das dort enthaltene Update-Skript ausführen.
7. Home Assistant prüfen und neu starten.
8. Site-Mapping und Pflichtsensoren kontrollieren.
9. `sensor.se_nf_config_check` und `sensor.se_nf_sanity_check` müssen `ok` melden.
10. Controller-Master erst danach wieder einschalten.

## Was wird übernommen?

Der neue Installer ersetzt die verwalteten Controller-Dateien und erstellt vorher ein dateibezogenes Backup. Lokale Entity-Zuordnungen und anlagenspezifische Einstellungen müssen über das neue Site-Mapping geprüft werden.

## Was wird nicht automatisch übernommen?

Private Automationen für Fahrzeug, Wallbox, Wärmepumpe, Shelly, Strompreis oder weitere lokale Geräte sind nicht Bestandteil des öffentlichen Projekts. Solche Funktionen bleiben lokal und werden bei Bedarf über neutrale Eingänge angebunden.

## Nach der Migration prüfen

Mindestens folgende Zustände kontrollieren:

```text
sensor.se_nf_config_check = ok
sensor.se_nf_sanity_check = ok
sensor.se_write_watchdog_status = ok
```

Bei Nutzung von EVOpt zusätzlich:

```text
sensor.se_nf_evopt_status = healthy
binary_sensor.se_nf_evopt_active_control = on
sensor.se_nf_evopt_candidate_source = evopt
```

## Support

Neue Fehlerberichte bitte ausschließlich hier erstellen:

**https://github.com/SolarEdgePS8/SolarEdge_HA_Energy_Controller/issues**
