SE NF Release Audit v2.9.8

1) Read-only Audit:
   /share/se_nf_release_audit/run_readonly.sh

2) Safe Functional A/B Tests:
   /share/se_nf_release_audit/run_safe_ab.sh

3) Alles zusammen:
   /share/se_nf_release_audit/run_all.sh

Reports:
   /share/se_nf_release_audit_reports/<timestamp>/

Wichtig:
- readonly verändert nichts.
- safe-ab verändert nur input_* Helfer temporär und stellt sie zurück.
- keine number.solaredge_* Schreibservices.
- safe-ab bricht ab, wenn Session nicht closed/armed oder target/desired nicht 0 sind.
