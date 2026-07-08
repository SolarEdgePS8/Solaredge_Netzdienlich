# Checklist before GitHub Publish

## Required

- [ ] ZIP generated successfully.
- [ ] SHA256 generated.
- [ ] Package files present.
- [ ] Audit suite present.
- [ ] README present.
- [ ] PORTING documentation present.
- [ ] ENTITY_MAPPING documentation present.
- [ ] CHANGELOG present.
- [ ] GitHub release body present.

## Home Assistant validation

- [ ] `ha core check` passed.
- [ ] `sensor.se_nf_config_check = ok`.
- [ ] `sensor.se_nf_sanity_check = ok`.
- [ ] `GATE_STATIC_MAIN_CRITICAL: PASS`.
- [ ] `critical_main: 0`.
- [ ] `GATE_RUNTIME: PASS`.
- [ ] `runtime_fail_count: 0`.
- [ ] `critical_internal: 0`.

## Release note

Mention clearly:

This is a Home-Assistant package bundle, not a HACS integration.
Users must map local SolarEdge, PV, consumption, forecast and weather entities before enabling.
