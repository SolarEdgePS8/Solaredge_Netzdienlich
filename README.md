# Solaredge_Netzdienlich – eingestellt

> **Dieses Repository wird nicht mehr weiterentwickelt.**  
> Die aktive Entwicklung wurde in das Nachfolgeprojekt **SolarEdge HA Energy Controller** überführt:
>
> **https://github.com/SolarEdgePS8/SolarEdge_HA_Energy_Controller**

## Was bedeutet das?

- keine neuen Funktionen oder Fehlerkorrekturen mehr in diesem Repository;
- keine Neuinstallation mehr auf Basis von `Solaredge_Netzdienlich`;
- bestehende Issues werden hier abgeschlossen;
- der Stand `v2.9.8` bleibt nur zur historischen Nachvollziehbarkeit erhalten;
- Installation, Updates, Dokumentation und Support erfolgen ausschließlich im neuen Projekt.

## Warum gibt es ein neues Projekt?

Der **SolarEdge HA Energy Controller** ist der technisch neu strukturierte Nachfolger. Er trennt Planung, Sicherheitsprüfung und Schreibzugriffe klar voneinander und unterstützt vier Betriebsarten:

1. **Eigenverbrauch maximieren**
2. **Netzdienlich laden**
3. **Akku schonen**
4. **EVOpt optimiert** mit Anbindung an den evcc Optimizer

Zusätzlich enthält das neue Projekt:

- zentrale Safety- und Arbiter-Logik;
- genau einen Writer je SolarEdge-Ziel;
- EVOpt-Startup-Handover und vollständigen Fallback;
- Write-Watchdog mit Writer- und Zustandsanalyse;
- portablen Installer, Update und Rollback;
- dokumentierte Site-Mappings;
- Release-Prüfungen und SHA256-Paritätsnachweis.

## Bestehende Installation umstellen

Bitte nicht einzelne Dateien aus beiden Projekten mischen. Verwende ausschließlich das vollständige Release des Nachfolgeprojekts.

Die Migrationsschritte stehen hier:

- [Migration zum SolarEdge HA Energy Controller](MIGRATION_TO_ENERGY_CONTROLLER.md)
- [Aktives Nachfolgeprojekt](https://github.com/SolarEdgePS8/SolarEdge_HA_Energy_Controller)
- [Releases des Nachfolgeprojekts](https://github.com/SolarEdgePS8/SolarEdge_HA_Energy_Controller/releases)

## Historischer Stand

Dieses Repository bleibt öffentlich, damit frühere Versionen, Diskussionen und Änderungen nachvollziehbar bleiben. Die enthaltenen Dateien sind jedoch **kein aktueller Installationsstand** mehr.

Für neue Fehlerberichte oder Funktionswünsche bitte das Issue-System des Nachfolgeprojekts verwenden:

**https://github.com/SolarEdgePS8/SolarEdge_HA_Energy_Controller/issues**
