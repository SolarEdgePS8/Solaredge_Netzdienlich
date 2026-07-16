# Veröffentlichung auf GitHub

## Windows-PowerShell-Veröffentlichung

Für v2.9.7 liegt ein separates PowerShell-Skript bei. Es verwendet die offizielle GitHub CLI und benötigt weder einen lokalen Git-Clone noch SSH.

Das Skript:

1. prüft Anmeldung, ZIP-Prüfsumme und Repository-Struktur,
2. baut einen vollständigen Git-Tree aus dem geprüften ZIP,
3. aktualisiert `main` erst nach der exakten Bestätigung `VERÖFFENTLICHEN`,
4. erzeugt Tag und Release `v2.9.7`,
5. lädt ZIP und SHA256-Datei als Assets hoch,
6. prüft Commit, Tag, Dashboard und Release-Assets online.

## GitHub Release

- Tag: `v2.9.7`
- Titel: `SolarEdge Netzdienlich Package v2.9.7`
- Beschreibung: `github/RELEASE_BODY_v2.9.7.md`
- Assets:
  - `SolarEdge_Netzdienlich_Package_v2.9.7.zip`
  - `SolarEdge_Netzdienlich_Package_v2.9.7.zip.sha256`

Bestehende Tags werden nicht verändert. Das Release-Skript bricht ab, wenn `v2.9.7` bereits existiert.
