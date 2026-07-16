#!/bin/sh
set -eu
BASE="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
CFG="${1:-$BASE/config/site_config.env}"

[ -f "$CFG" ] || {
  echo "Konfiguration fehlt: $CFG"
  echo "Kopiere zuerst config/site_config.env.example nach config/site_config.env."
  exit 1
}

set -a
. "$CFG"
set +a

[ "${SITE_CONFIG_CONFIRMED:-NO}" = "YES" ] || {
  echo "ABBRUCH: SITE_CONFIG_CONFIRMED muss nach Prüfung auf YES gesetzt werden."
  exit 1
}

: "${SUPERVISOR_TOKEN:?SUPERVISOR_TOKEN fehlt}"
API="http://supervisor/core/api"

set_text() {
  entity="$1"
  value="$2"
  [ -n "$value" ] || return 0
  echo "SET TEXT: $entity = $value"
  curl -fsS -X POST \
    -H "Authorization: Bearer $SUPERVISOR_TOKEN" \
    -H "Content-Type: application/json" \
    "$API/services/input_text/set_value" \
    -d "{\"entity_id\":\"$entity\",\"value\":\"$value\"}" >/dev/null
}


set_text_optional() {
 entity="$1"
 value="${2-}"
 echo "SET OPTIONAL TEXT: $entity = ${value:-<leer>}"
 curl -fsS -X POST \
 -H "Authorization: Bearer $SUPERVISOR_TOKEN" \
 -H "Content-Type: application/json" \
 "$API/services/input_text/set_value" \
 -d "{\"entity_id\":\"$entity\",\"value\":\"$value\"}" >/dev/null
}

set_number() {
  entity="$1"
  value="$2"
  [ -n "$value" ] || return 0
  echo "SET NUMBER: $entity = $value"
  curl -fsS -X POST \
    -H "Authorization: Bearer $SUPERVISOR_TOKEN" \
    -H "Content-Type: application/json" \
    "$API/services/input_number/set_value" \
    -d "{\"entity_id\":\"$entity\",\"value\":$value}" >/dev/null
}

# Mappings
set_text input_text.se_nf_charge_limit_entity "$CHARGE_LIMIT_ENTITY"
set_text input_text.se_nf_discharge_limit_entity "${DISCHARGE_LIMIT_ENTITY:-}"
set_text input_text.se_nf_battery_soe_entity "$BATTERY_SOE_ENTITY"
set_text input_text.se_nf_battery_capacity_entity "$BATTERY_CAPACITY_ENTITY"
set_text input_text.se_nf_backup_reserve_entity "$BACKUP_RESERVE_ENTITY"
set_text input_text.se_nf_pv_today_remaining_entity "$PV_TODAY_REMAINING_ENTITY"
set_text input_text.se_nf_pv_today_total_entity "$PV_TODAY_TOTAL_ENTITY"
set_text input_text.se_nf_pv_tomorrow_entity "$PV_TOMORROW_ENTITY"
set_text input_text.se_nf_pv_overmorrow_entities "${PV_OVERMORROW_ENTITIES:-}"
set_text input_text.se_nf_forecast_now_entity "${FORECAST_NOW_ENTITY:-}"
set_text input_text.se_nf_weather_entity "$WEATHER_ENTITY"
set_text input_text.se_nf_live_pv_power_entities "$LIVE_PV_POWER_ENTITIES"
set_text input_text.se_nf_live_consumption_power_entities "$LIVE_CONSUMPTION_POWER_ENTITIES"
set_text_optional input_text.se_nf_actual_pv_today_entities "${ACTUAL_PV_TODAY_ENTITIES:-}"
set_text_optional input_text.se_nf_daily_consumption_entity "${DAILY_CONSUMPTION_ENTITY:-}"
set_text_optional input_text.se_nf_pv_actual_meter_source_entity "${PV_ACTUAL_METER_SOURCE_ENTITY:-}"
set_text_optional input_text.se_nf_evcc_battery_mode_entity "${EVCC_BATTERY_MODE_ENTITY:-}"
set_text input_text.se_nf_sql_db_path "${SQL_DB_PATH:-/config/home-assistant_v2.db}"

# Einmalige Parameter
set_number input_number.se_nf_max_sensor_age_s "$MAX_SENSOR_AGE_S"
set_number input_number.se_nf_closed_charge_limit_w "$CLOSED_CHARGE_LIMIT_W"
set_number input_number.se_nf_open_charge_limit_w "$OPEN_CHARGE_LIMIT_W"
set_number input_number.se_nf_target_soc_pct "$TARGET_SOC_PCT"
set_number input_number.se_nf_planning_charge_power_w "$PLANNING_CHARGE_POWER_W"
set_number input_number.se_nf_start_safety_buffer_min "$START_SAFETY_BUFFER_MIN"
set_number input_number.se_nf_min_start_hour "$MIN_START_HOUR"
set_number input_number.se_nf_latest_finish_hour "$LATEST_FINISH_HOUR"
set_number input_number.se_nf_session_end_grace_min "$SESSION_END_GRACE_MIN"
set_number input_number.se_nf_low_soc_floor_pct "$LOW_SOC_FLOOR_PCT"
set_number input_number.se_nf_manual_daily_consumption_kwh "$MANUAL_DAILY_CONSUMPTION_KWH"
set_number input_number.se_nf_load_forecast_safety_factor "$LOAD_FORECAST_SAFETY_FACTOR"
set_number input_number.se_nf_coverage_lead_max_min "$COVERAGE_LEAD_MAX_MIN"
set_number input_number.se_nf_weather_current_weight_pct "$WEATHER_CURRENT_WEIGHT_PCT"
set_number input_number.se_nf_weather_missing_forecast_factor "$WEATHER_MISSING_FORECAST_FACTOR"
set_number input_number.se_nf_weather_max_lead_min "$WEATHER_MAX_LEAD_MIN"
set_number input_number.se_nf_replan_threshold_min "$REPLAN_THRESHOLD_MIN"
set_number input_number.se_nf_write_min_delta_w "$WRITE_MIN_DELTA_W"
set_number input_number.se_nf_write_cooldown_s "$WRITE_COOLDOWN_S"
set_number input_number.se_nf_write_lock_s "$WRITE_LOCK_S"
set_number input_number.se_nf_lifetime_min_start_hour "$LIFETIME_MIN_START_HOUR"
set_number input_number.se_nf_lifetime_latest_finish_hour "$LIFETIME_LATEST_FINISH_HOUR"
set_number input_number.se_nf_lifetime_start_safety_buffer_min "$LIFETIME_START_SAFETY_BUFFER_MIN"
set_number input_number.se_nf_lifetime_min_soc_pct "$LIFETIME_MIN_SOC_PCT"
set_number input_number.se_nf_lifetime_max_soc_pct "$LIFETIME_MAX_SOC_PCT"
set_number input_number.se_nf_lifetime_min_target_soc_pct "$LIFETIME_MIN_TARGET_SOC_PCT"
set_number input_number.se_nf_lifetime_max_target_soc_pct "$LIFETIME_MAX_TARGET_SOC_PCT"
set_number input_number.se_nf_lifetime_safety_kwh "$LIFETIME_SAFETY_KWH"
set_number input_number.se_nf_lifetime_night_fallback_kwh "$LIFETIME_NIGHT_FALLBACK_KWH"
set_number input_number.se_nf_lifetime_soc_buffer_pct "$LIFETIME_SOC_BUFFER_PCT"
set_number input_number.se_nf_early_open_deficit_kwh "$EARLY_OPEN_DEFICIT_KWH"

echo
echo "Master wurde NICHT aktiviert."
echo "Warte 20 Sekunden, dann erster Check ..."
sleep 20
"$BASE/scripts/run_first_checks.sh"
