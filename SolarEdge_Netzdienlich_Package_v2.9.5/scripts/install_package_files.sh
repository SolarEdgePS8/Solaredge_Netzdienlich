#!/bin/sh
set -eu

BASE="$(cd "$(dirname "$0")/.." && pwd)"
DEST="/config/packages"

echo "Installing package files from: $BASE/package"
echo "Destination: $DEST"

mkdir -p "$DEST"

cp "$BASE/package/solaredge_netzdienlich.yaml" "$DEST/"
cp "$BASE/package/se_nf_07_writer_safety.yaml" "$DEST/"
cp "$BASE/package/se_nf_08_planning_helpers.yaml" "$DEST/"
cp "$BASE/package/se_nf_09_lifetime_target_helpers.yaml" "$DEST/"

echo "Done. Now run:"
echo "ha core check"
