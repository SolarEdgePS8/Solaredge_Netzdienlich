#!/bin/sh
set -eu
BASE="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
DEST="/share/se_nf_release_audit"

rm -rf "$DEST"
mkdir -p "$DEST"
cp -R "$BASE/audit/." "$DEST/"
chmod +x "$DEST"/*.sh "$DEST"/*.py 2>/dev/null || true

cat > "$DEST/release_manifest.txt" <<'EOF'
/config/packages/solaredge_netzdienlich.yaml
/config/packages/se_nf_07_writer_safety.yaml
/config/packages/se_nf_08_planning_helpers.yaml
/config/packages/se_nf_10_dynamic_night_forecast.yaml
/config/packages/se_nf_13_resilience_target.yaml
/config/se_nf_load_forecast_7d_cached.py
/config/se_nf_night_forecast_7d.py
/config/se_nf_daytime_forecast_7d.py
EOF

echo "Audit-Suite installiert: $DEST"
