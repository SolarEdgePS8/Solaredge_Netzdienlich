#!/bin/sh
set -eu
BASE="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
CONFIG_DEST="${SE_NF_CONFIG_ROOT:-/config}"
SHARE_DEST="${SE_NF_SHARE_ROOT:-/share}"
PACKAGE_DEST="$CONFIG_DEST/packages"
TS="$(date +%Y%m%d_%H%M%S)"
BACKUP="$SHARE_DEST/se_nf_install_backup_$TS"

mkdir -p "$PACKAGE_DEST" "$CONFIG_DEST" "$BACKUP/packages" "$BACKUP/runtime"

PACKAGE_FILES="
  solaredge_netzdienlich.yaml \
  se_nf_07_writer_safety.yaml \
  se_nf_08_planning_helpers.yaml \
  se_nf_10_dynamic_night_forecast.yaml \
  se_nf_13_resilience_target.yaml
"

RUNTIME_FILES="
  se_nf_load_forecast_7d_cached.py \
  se_nf_night_forecast_7d.py \
  se_nf_daytime_forecast_7d.py
"

OBSOLETE_PACKAGE_FILES="
  se_nf_09_lifetime_target_helpers.yaml \
  se_nf_11_dynamic_target_preview.yaml \
  se_nf_14_resilience_refresh.yaml \
  se_nf_quiet_logging.yaml
"

for file in $PACKAGE_FILES
do
  [ -f "$BASE/package/$file" ] || { echo "FEHLT: $BASE/package/$file"; exit 1; }
done

for file in $RUNTIME_FILES
do
  source="$BASE/scripts/runtime/$file"
  [ -f "$source" ] || { echo "FEHLT: $source"; exit 1; }
  python3 - "$source" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
compile(path.read_text(encoding="utf-8"), str(path), "exec")
PY
done

for file in $PACKAGE_FILES
do
  [ ! -f "$PACKAGE_DEST/$file" ] || cp "$PACKAGE_DEST/$file" "$BACKUP/packages/$file"
  install -m 0644 "$BASE/package/$file" "$PACKAGE_DEST/$file"
  echo "INSTALLIERT: $PACKAGE_DEST/$file"
done

for file in $RUNTIME_FILES
do
  [ ! -f "$CONFIG_DEST/$file" ] || cp "$CONFIG_DEST/$file" "$BACKUP/runtime/$file"
  install -m 0755 "$BASE/scripts/runtime/$file" "$CONFIG_DEST/$file"
  echo "INSTALLIERT: $CONFIG_DEST/$file"
done

for file in $OBSOLETE_PACKAGE_FILES
do
  if [ -f "$PACKAGE_DEST/$file" ]; then
    mv "$PACKAGE_DEST/$file" "$BACKUP/packages/$file"
    echo "DEAKTIVIERT UND GESICHERT: $PACKAGE_DEST/$file"
  fi
done

echo
echo "Backup: $BACKUP"
echo "Python-Helfer: Syntaxprüfung erfolgreich"
echo "Nächster Schritt: ha core check"
