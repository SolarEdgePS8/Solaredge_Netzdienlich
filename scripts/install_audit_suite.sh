#!/bin/sh
set -eu
BASE="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
DEST="/share/se_nf_release_audit_v296"

rm -rf "$DEST"
mkdir -p "$DEST"
cp -R "$BASE/audit/." "$DEST/"
chmod +x "$DEST"/*.sh "$DEST"/*.py 2>/dev/null || true

cat > "$DEST/release_manifest.txt" <<'EOF'
/config/packages/solaredge_netzdienlich.yaml
/config/packages/se_nf_07_writer_safety.yaml
/config/packages/se_nf_08_planning_helpers.yaml
/config/packages/se_nf_09_lifetime_target_helpers.yaml
EOF

echo "Audit-Suite installiert: $DEST"
