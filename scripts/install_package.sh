#!/bin/sh
set -eu
BASE="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
DEST="/config/packages"
TS="$(date +%Y%m%d_%H%M%S)"
BACKUP="/share/se_nf_install_backup_$TS"

mkdir -p "$DEST" "$BACKUP"

for file in \
  solaredge_netzdienlich.yaml \
  se_nf_07_writer_safety.yaml \
  se_nf_08_planning_helpers.yaml \
  se_nf_09_lifetime_target_helpers.yaml
do
  [ -f "$BASE/package/$file" ] || { echo "FEHLT: $BASE/package/$file"; exit 1; }
  [ ! -f "$DEST/$file" ] || cp "$DEST/$file" "$BACKUP/$file"
  cp "$BASE/package/$file" "$DEST/$file"
  echo "INSTALLIERT: $DEST/$file"
done

echo
echo "Backup: $BACKUP"
echo "Nächster Schritt: ha core check"
