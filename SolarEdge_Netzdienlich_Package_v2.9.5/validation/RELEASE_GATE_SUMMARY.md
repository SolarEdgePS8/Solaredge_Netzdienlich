# Release Gate Summary v2.9.5

## Passed

```text
GATE_STATIC_MAIN_CRITICAL: PASS
critical_main: 0
GATE_RUNTIME: PASS
runtime_fail_count: 0
GATE_MANIFEST: PASS_OR_EXTERNAL_REVIEW
critical_internal: 0
```

## External review required

These SolarEdge entities are installation-specific and must exist or be mapped:

```text
number.solaredge_i1_backup_reserve
number.solaredge_i1_storage_charge_limit
sensor.solaredge_i1_b1_state_of_energy
```

Local sensors must be mapped using `input_text.se_nf_*` helpers.
