/*
 *
 * Copyright 2017-present Facebook. All Rights Reserved.
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
 */

#include <stdio.h>
#include <stdlib.h>
#include <syslog.h>
#include <string.h>
#include <stdbool.h>
#include <assert.h>
#include <openbmc/obmc-sensor.h>
#include <openbmc/edb.h>
#include <jansson.h>
#include "aggregate-sensor-internal.h"

#define PRINT(slog, fmt, ...) do { \
  if (slog) { \
    syslog(LOG_INFO, fmt, ##__VA_ARGS__); \
  } else { \
    printf(fmt, ##__VA_ARGS__); \
  } \
} while(0)

#define DEFAULT_CONF_FILE_PATH "/etc/aggregate-sensor-conf.json"

size_t g_sensors_count = 0;
aggregate_sensor_t *g_sensors = NULL;

int get_sensor_value(void *state, float *value)
{
  struct sensor_src *snr = (struct sensor_src *)state;
  assert(snr);
  assert(value);
  return sensor_cache_read(snr->fru, snr->id, value);
}

int
aggregate_sensor_count(size_t *count)
{
  *count = g_sensors_count;
  return 0;
}

int
aggregate_sensor_read(size_t index, float *value)
{
  char cond_value[MAX_VALUE_LEN];
  size_t i;
  aggregate_sensor_t *snr;
  if (index >= g_sensors_count) {
    return -1;
  }
  snr = &g_sensors[index];
  if (edb_cache_get(snr->cond_key, cond_value)) {
    if (snr->default_expression_idx != -1) {
      size_t f_idx = snr->default_expression_idx;
      return expression_evaluate(snr->expressions[f_idx], value);
    }
    DEBUG("key: %s not available\n", snr->cond_key);
    return -1;
  }
  for (i = 0; i < snr->value_map_size; i++) {
    if (!strncmp(snr->value_map[i].condition_value, cond_value,
          sizeof(snr->value_map[i].condition_value))) {
      size_t f_idx = snr->value_map[i].formula_index;
      return expression_evaluate(snr->expressions[f_idx], value);
    }
  }
  if (snr->default_expression_idx != -1) {
    size_t f_idx = (size_t)snr->default_expression_idx;
    return expression_evaluate(snr->expressions[f_idx], value);
  }
  return -1;
}

int
aggregate_sensor_threshold(size_t index, thresh_sensor_t *thresh)
{
  if (index >= g_sensors_count) {
    return -1;
  }
  
  *thresh = g_sensors[index].sensor;
  return 0;
}

int
aggregate_sensor_name(size_t index, char *name)
{
  if (index >= g_sensors_count) {
    return -1;
  }
  strncpy(name, g_sensors[index].sensor.name, MAX_STRING_SIZE);
  return 0;
}

int
aggregate_sensor_units(size_t index, char *units)
{
  if (index >= g_sensors_count) {
    return -1;
  }
  strncpy(units, g_sensors[index].sensor.units, MAX_STRING_SIZE);
  return 0;
}

int
aggregate_sensor_init(const char *conf_file_path)
{
  if (!conf_file_path) {
    conf_file_path = DEFAULT_CONF_FILE_PATH;
  }
  return load_aggregate_conf(conf_file_path);
}

void
aggregate_sensor_conf_print(bool slog)
{
  size_t i;
  PRINT(slog, "Found: %zu sensors\n", g_sensors_count);
  for (i = 0; i < g_sensors_count; i++) {
    aggregate_sensor_t *snr = &g_sensors[i];
    size_t j;
    PRINT(slog, "Name: %s\n", snr->sensor.name);
    PRINT(slog, "Unit: %s\n", snr->sensor.units);
    PRINT(slog, "idx: %zu\n", snr->idx);
    PRINT(slog, "cond_key: %s\n", snr->cond_key);
    PRINT(slog, "Expressions: (%zu)\n", snr->num_expressions);
    for (j = 0; j < snr->num_expressions; j++) {
      expression_print(snr->expressions[j]);
      printf("\n");
    }
    PRINT(slog, "Default expression IDX: %d\n", snr->default_expression_idx);
    PRINT(slog, "Conditions:\n");
    for (j = 0; j < snr->value_map_size; j++) {
      PRINT(slog, "%s => %zu\n", 
          snr->value_map[j].condition_value,
          snr->value_map[j].formula_index);
    }
    PRINT(slog, "Thresholds: ");
    if (snr->sensor.flag & GETMASK(UCR_THRESH))
      PRINT(slog, "UCR: %5.5f ", snr->sensor.ucr_thresh);
    else
      PRINT(slog, "UCR: NA ");
    if (snr->sensor.flag & GETMASK(UNC_THRESH))
      PRINT(slog, "UNC: %5.5f ", snr->sensor.unc_thresh);
    else
      PRINT(slog, "UNC: NA ");
    if (snr->sensor.flag & GETMASK(UNR_THRESH))
      PRINT(slog, "UNR: %5.5f ", snr->sensor.unr_thresh);
    else
      PRINT(slog, "UNR: NA ");
    if (snr->sensor.flag & GETMASK(LCR_THRESH))
      PRINT(slog, "LCR: %5.5f ", snr->sensor.lcr_thresh);
    else
      PRINT(slog, "LCR: NA ");
    if (snr->sensor.flag & GETMASK(LNC_THRESH))
      PRINT(slog, "LNC: %5.5f ", snr->sensor.lnc_thresh);
    else
      PRINT(slog, "LNC: NA ");
    if (snr->sensor.flag & GETMASK(LNR_THRESH))
      PRINT(slog, "LNR: %5.5f ", snr->sensor.lnr_thresh);
    else
      PRINT(slog, "UCR: NA ");
    PRINT(slog, "\n");

    PRINT(slog, "-------------------------\n");
  }
}

