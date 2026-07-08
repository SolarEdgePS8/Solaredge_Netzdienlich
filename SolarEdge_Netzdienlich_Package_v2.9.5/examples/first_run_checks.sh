#!/bin/sh
echo "=== SE NF first run checks ==="

for e in \
sensor.se_nf_config_check \
sensor.se_nf_sanity_check \
sensor.se_nf_today_charge_window \
sensor.se_nf_decision_reason \
sensor.se_nf_charge_limit_target \
sensor.se_nf_charge_limit_actual \
sensor.se_nf_writer_mode \
input_boolean.se_netzdienlich_enabled
do
  echo
  echo "### $e"
  curl -sS -H "Authorization: Bearer $SUPERVISOR_TOKEN" \
    "http://supervisor/core/api/states/$e"
done
