# 01 – Erstinstallation auf einer neuen Home-Assistant-Instanz

Diese Anleitung gilt für eine Instanz, auf der das Package noch nie installiert war.

## Voraussetzungen

- Home Assistant mit aktiviertem Package-Support
- SolarEdge-Integration mit beschreibbarem Charge-Limit
- Terminal/SSH-Add-on
- `git` ist hilfreich, aber nicht zwingend

## 1. Package-Support aktivieren

In `/config/configuration.yaml`:

```yaml
homeassistant:
  packages: !include_dir_named packages
```

## 2. Repository klonen

Beispiel:

```bash
mkdir -p /config/repos
cd /config/repos
git clone https://github.com/SolarEdgePS8/Solaredge_Netzdienlich.git
cd Solaredge_Netzdienlich
```

Alternativ das Release-ZIP entpacken.

## 3. Package-Dateien installieren

```bash
chmod +x scripts/*.sh
./scripts/install_package.sh
ha core check
```

Nur bei erfolgreichem Check:

```bash
ha core restart
```

## 4. Lokale Entity-Zuordnung erstellen

```bash
cp config/site_config.env.example config/site_config.env
```

Dann `config/site_config.env` mit VS Code bearbeiten.

Die Pflichtfelder müssen auf die eigene Instanz zeigen. Der Discovery-Helfer kann Kandidaten anzeigen:

```bash
python3 scripts/discover_entities.py
```

## 5. Konfiguration anwenden

Nach vollständiger Prüfung in `site_config.env`:

```text
SITE_CONFIG_CONFIRMED=YES
```

Danach:

```bash
./scripts/apply_site_config.sh
```

Das Script:

- setzt die lokalen Mapping-Helfer,
- setzt sinnvolle Startwerte einmalig,
- aktiviert den Master-Schalter nicht,
- prüft die angegebenen Entities.

## 6. Audit-Suite installieren und ausführen

```bash
./scripts/install_audit_suite.sh
/share/se_nf_release_audit/run_readonly.sh
/share/se_nf_release_audit/se_nf_manifest_audit.py
```

## 7. Ergebnis prüfen

Erforderlich:

```text
sensor.se_nf_config_check = ok
sensor.se_nf_sanity_check = ok
```

`writer_mode` kann je nach Situation `idle`, `normal`, `blocked_cooldown` oder einen anderen erklärbaren Zustand anzeigen. `normal` ist nicht automatisch ein Fehler.

## 8. Erst jetzt aktivieren

```bash
curl -sS -X POST   -H "Authorization: Bearer $SUPERVISOR_TOKEN"   -H "Content-Type: application/json"   http://supervisor/core/api/services/input_boolean/turn_on   -d '{"entity_id":"input_boolean.se_netzdienlich_enabled"}'
```
