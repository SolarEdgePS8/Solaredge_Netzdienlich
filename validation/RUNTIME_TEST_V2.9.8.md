# Runtime-Abnahme v2.9.8

Testdatum: 2026-07-17  
Quelle: exakter v2.9.8-RC1 auf lokaler Home-Assistant-Referenzinstanz  
Datenschutz: nur zusammengefasste Ergebnisse; keine Tokens, Hosts,
Entity-Mappings oder vollständigen Messreihen

## Vollständiger Moduswechseltest

Der ausführende Tester V2 isolierte die physischen Writer, schaltete
nacheinander alle drei Modi und stellte den ursprünglichen Zustand
anschließend wieder her.

```text
Modi: Eigenverbrauch maximieren, Netzdienlich laden, Akku schonen
Prüfungen: 79
Bestanden: 79
Fehlgeschlagen: 0
Cleanup: erfolgreich
Physisches Charge-Limit: unverändert
Ergebnis: PASS
```

Geprüft wurden unter anderem Zielquelle, benötigte Energie, Ladedauer,
Modusparameter, heutiger und morgiger Start, persistierter Start, aktiver Start,
Fensterreihenfolge sowie das erwartete Verhalten des Session-Managers.

## Resilienztest

```text
Prüfungen: 29
Bestanden: 29
Fehlgeschlagen: 0
Ergebnis: PASS
```

Geprüft wurden dynamisch verbundene Tag-/Nachtfenster, Median-Historie,
Backup-Pfad, Zielgleichheit, unabhängige Nachrechnung, monotones Verhalten bei
weniger PV und mehr Puffer sowie das Kapazitätsrisiko.

Die dynamische Grenze lag im Abnahmelauf bei `07:20`; Nachtfenster
`18:30–07:20` und Tagesfenster `07:20–18:30` schlossen lückenlos aneinander an.

## Offline-Nachprüfung des bereinigten Release-Kandidaten

```text
Statische Release-Prüfungen: 36/36 PASS
Randomisierte Resilienzfälle: 100000 PASS
Isolierter Neu-/Update-Installertest: PASS
Synthetischer Recorder-Test: PASS
```

Der bereinigte Kandidat wurde anschließend auf der
Home-Assistant-Referenzinstanz installiert. `ha core check`, Config-/Sanity,
Resilienzprüfung und vollständige Runtime-Abnahme waren erfolgreich.
