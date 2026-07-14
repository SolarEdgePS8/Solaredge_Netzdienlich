# Privacy note

The public release contains only a sanitized validation summary.

Raw audit reports are intentionally not included because they can contain
installation-specific entity names, timestamps, sensor values and local paths.

Users can generate fresh reports on their own Home Assistant instance with:

```bash
./scripts/install_audit_suite.sh
/share/se_nf_release_audit_v296/run_readonly.sh
/share/se_nf_release_audit_v296/se_nf_manifest_audit.py
```
