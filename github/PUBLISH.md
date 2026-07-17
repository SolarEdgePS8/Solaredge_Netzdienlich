# Veröffentlichung auf GitHub

## Veröffentlichungsablauf

Für v2.9.8 wird ausschließlich der vollständig geprüfte Repository-Stand veröffentlicht. Vor dem Tag müssen Installer-, Manifest-, Datenschutz- und Runtime-Gates bestanden sein.

Der Ablauf:

1. prüft Anmeldung, ZIP-Prüfsumme und Repository-Struktur,
2. baut einen vollständigen Git-Tree aus dem geprüften ZIP,
3. aktualisiert `main` erst nach der exakten Bestätigung `VERÖFFENTLICHEN`,
4. erzeugt Tag und Release `v2.9.8`,
5. lädt ZIP und SHA256-Datei als Assets hoch,
6. prüft Commit, Tag, Dashboard und Release-Assets online.

## GitHub Release

- Tag: `v2.9.8`
- Titel: `SolarEdge Netzdienlich Package v2.9.8`
- Beschreibung: `github/RELEASE_BODY_v2.9.8.md`
- Assets:
  - `SolarEdge_Netzdienlich_Package_v2.9.8.zip`
  - `SolarEdge_Netzdienlich_Package_v2.9.8.zip.sha256`

Bestehende Tags werden nicht verändert. Die Veröffentlichung bricht ab, wenn `v2.9.8` bereits existiert.
