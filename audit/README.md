# Audit-Suite v2.9.7

Die Python-Dateien sind Prüfwerkzeuge und keine Home-Assistant-Integrationen.

## Welches Script wofür?

- `run_readonly.sh`: sicherer Standardtest; verändert keine Helfer und schreibt nicht auf SolarEdge.
- `se_nf_manifest_audit.py`: prüft nur die vier Release-Package-Dateien auf interne Abhängigkeiten und Portabilität.
- `run_safe_ab.sh`: verändert temporär ausgewählte `input_*`-Helfer, vergleicht die Auswirkungen und stellt die Werte zurück. Nur bei ruhigem Systemzustand verwenden.
- `run_all.sh`: kombiniert Read-only und Safe-A/B. Für die Erstinstallation ist zunächst `run_readonly.sh` ausreichend.

## Installation auf Home Assistant

Den kompletten Ordner nach `/share/se_nf_release_audit/` kopieren.

## Ausführen

```bash
/share/se_nf_release_audit/run_readonly.sh
/share/se_nf_release_audit/se_nf_manifest_audit.py
```

Reports werden unter `/share/se_nf_release_audit_reports/<Zeitstempel>/` abgelegt.
