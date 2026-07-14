# Veröffentlichung auf GitHub

## Bestehenden lokalen Clone sauber ersetzen

```bash
rsync -a --delete --exclude '.git/'   /share/Solaredge_Netzdienlich_v2.9.6_repo/   /PFAD/ZUM/GEKLONTEN/REPO/

cd /PFAD/ZUM/GEKLONTEN/REPO
git status
git add -A
git commit -m "Release v2.9.6"
git push
```

## GitHub Release

- Tag: `v2.9.6`
- Titel: `SolarEdge Netzdienlich Package v2.9.6`
- Beschreibung: `github/RELEASE_BODY_v2.9.6.md`
- Assets:
  - `SolarEdge_Netzdienlich_Package_v2.9.6.zip`
  - `SolarEdge_Netzdienlich_Package_v2.9.6.zip.sha256`

Bestehende Tags sollten nicht nachträglich verändert werden. Das vorherige Release bleibt als Versionshistorie erhalten.
