#!/bin/sh
set -eu
: "${SUPERVISOR_TOKEN:?SUPERVISOR_TOKEN fehlt}"
API="http://supervisor/core/api"

for entity in \
  sensor.se_nf_config_check \
  sensor.se_nf_sanity_check \
  sensor.se_nf_writer_mode \
  sensor.se_nf_charge_limit_target \
  sensor.se_nf_desired_target \
  sensor.se_nf_charge_limit_actual \
  sensor.se_nf_soe_age_s \
  sensor.se_nf_charge_limit_age_s \
  sensor.se_nf_today_charge_window \
  sensor.se_nf_decision_reason \
  input_boolean.se_netzdienlich_enabled
do
  echo
  echo "### $entity"
  curl -fsS \
    -H "Authorization: Bearer $SUPERVISOR_TOKEN" \
    "$API/states/$entity"
done

echo
echo "Hinweis: writer_mode=normal kann gültig sein. Config Check und Sanity Check müssen vor Aktivierung ok sein."
