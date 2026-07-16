# 06 – GitHub-, VS-Code- und SSH-Workflow

## Erstmals klonen

```bash
mkdir -p /config/repos
cd /config/repos
git clone https://github.com/SolarEdgePS8/Solaredge_Netzdienlich.git
cd Solaredge_Netzdienlich
```

Den geklonten Ordner kann man mit dem VS-Code-Add-on bearbeiten.

## Installation aus dem Clone

```bash
./scripts/install_package.sh
ha core check
ha core restart
```

## Spätere Updates

```bash
cd /config/repos/Solaredge_Netzdienlich
git pull --ff-only
./scripts/install_package.sh
ha core check
ha core restart
```

## Warum nicht direkt aus dem Git-Ordner laden?

Die eigentlichen Package-Dateien liegen bewusst weiterhin unter `/config/packages`. Das Repository bleibt eine saubere Quelle, während Home Assistant aus dem etablierten Package-Ordner lädt.

## FileZilla

FileZilla kann weiterhin für Backups oder einmalige Dateiübertragungen verwendet werden. Für wiederkehrende Updates ist `git pull` nachvollziehbarer und reduziert manuelle Kopierfehler.

## Eigenes Repository sauber aktualisieren

Der Release-Builder erzeugt unter `/share` einen sauberen Repo-Ordner. Zum Ersetzen eines lokalen Git-Clones:

```bash
rsync -a --delete --exclude '.git/'   /share/Solaredge_Netzdienlich_v2.9.7_repo/   /PFAD/ZUM/GEKLONTEN/REPO/

cd /PFAD/ZUM/GEKLONTEN/REPO
git add -A
git commit -m "Release v2.9.7"
git push
```

`--delete` entfernt alte, im neuen Release nicht mehr enthaltene doppelte Dokumente und Backup-Dateien. Vorher den Zielpfad genau prüfen.
