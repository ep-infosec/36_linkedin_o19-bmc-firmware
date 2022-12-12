/* Copyright 2015-present Facebook. All Rights Reserved.
 *
 * This file contains code to support IPMI2.0 Specificaton available @
 * http://www.intel.com/content/www/us/en/servers/ipmi/ipmi-specifications.html
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
#include <stdint.h>
#include <syslog.h>
#include "fby2_gpio.h"

// List of TL GPIO pins to be monitored
const uint8_t gpio_pin_list[] = {
  PWRGD_COREPWR,
  PWRGD_PCH_PWROK,
  PVDDR_AB_VRHOT_N,
  PVDDR_DE_VRHOT_N,
  PVCCIN_VRHOT_N,
  FM_THROTTLE_N,
  FM_PCH_BMC_THERMTRIP_N,
  H_MEMHOT_CO_N,
  FM_CPU0_THERMTRIP_LVT3_N,
  CPLD_PCH_THERMTRIP,
  FM_CPLD_FIVR_FAULT,
  FM_CPU_CATERR_N,
  FM_CPU_ERROR_2,
  FM_CPU_ERROR_1,
  FM_CPU_ERROR_0,
  FM_SLPS4_N,
  FM_NMI_EVENT_BMC_N,
  FM_SMI_BMC_N,
  PLTRST_N,
  FP_RST_BTN_N,
  RST_BTN_BMC_OUT_N,
  FM_BIOS_POST_COMPT_N,
  FM_SLPS3_N,
  PWRGD_PVCCIN,
  FM_BACKUP_BIOS_SEL_N,
  FM_EJECTOR_LATCH_DETECT_N,
  BMC_RESET,
  FM_JTAG_BIC_TCK_MUX_SEL_N,
  BMC_READY_N,
  BMC_COM_SW_N,
  RST_I2C_MUX_N,
  XDP_BIC_PREQ_N,
  XDP_BIC_TRST,
  FM_SYS_THROTTLE_LVC3,
  XDP_BIC_PRDY_N,
  XDP_PRSNT_IN_N,
  XDP_PRSNT_OUT_N,
  XDP_BIC_PWR_DEBUG_N,
  FM_BIC_JTAG_SEL_N,
};

size_t gpio_pin_cnt = sizeof(gpio_pin_list)/sizeof(uint8_t);
const uint32_t gpio_ass_val = 0x0 | (1 << FM_CPLD_FIVR_FAULT);

// List of RC GPIO pins to be monitored
const uint8_t rc_gpio_pin_list[] = {
  RC_PWRGD_SYS_PWROK,
  RC_QDF_PS_HOLD_OUT,
  RC_PVDDQ_510_VRHOT_N_R1,
  RC_PVDDQ_423_VRHOT_N_R1,
  RC_VR_I2C_SEL,
  RC_QDF_THROTTLE_3P3_N,
  RC_QDF_FORCE_PMIN,
  RC_QDF_FORCE_PSTATE,
  RC_QDF_TEMPTRIP_N,
  RC_FAST_THROTTLE_N,
  RC_QDF_LIGHT_THROTTLE_3P3_N,
  RC_UEFI_DB_MODE_N,
  RC_QDF_RAS_ERROR_2,
  RC_QDF_RAS_ERROR_1,
  RC_QDF_RAS_ERROR_0,
  RC_SPI_MUX_SEL,
  RC_QDF_NMI,
  RC_QDF_SMI,
  RC_QDF_RES_OUT_N_R,
  RC_SYS_BUF_RST_N,
  RC_SYS_BIC_RST_N,
  RC_FM_BIOS_POST_CMPLT_N,
  RC_IMC_RDY,
  RC_PWRGD_PS_PWROK,
  RC_FM_BACKUP_BIOS_SEL_N,
  RC_T32_JTAG_DET,
  RC_BB_BMC_RST_N,
  RC_QDF_PRSNT_0_N,
  RC_QDF_PRSNT_1_N,
  RC_EJCT_DET_N,
  RC_M2_I2C_MUX_RST_N,
  RC_BIC_REMOTE_SRST_N,
  RC_BIC_DB_TRST_N,
  RC_IMC_BOOT_ERROR,
  RC_BIC_RDY,
  RC_QDF_PROCHOT_N,
  RC_PWR_BIC_BTN_N,
  RC_PWR_BTN_BUF_N,
  RC_PMF_REBOOT_REQ_N,
  RC_BIC_BB_I2C_ALERT,
};
size_t rc_gpio_pin_cnt = sizeof(rc_gpio_pin_list)/sizeof(uint8_t);

// List of EP GPIO pins to be monitored
const uint8_t ep_gpio_pin_list[] = {
  EP_PWRGD_COREPWR,
  EP_PWRGD_SYS_PWROK,
  EP_PWRGD_PS_PWROK_PLD,
  EP_PVCCIN_VRHOT_N,
  EP_H_MEMHOT_CO_N,
  EP_FM_CPLD_BIC_THERMTRIP_N,
  EP_FM_CPU_ERROR_2,
  EP_FM_CPU_ERROR_1,
  EP_FM_CPU_ERROR_0,
  EP_FM_NMI_EVENT_BMC_N,
  EP_FM_CRASH_DUMP_M3_N,
  EP_FP_RST_BTN_N,
  EP_FP_RST_BTN_OUT_N,
  EP_FM_BIOS_POST_COMPT_N,
  EP_FM_BACKUP_BIOS_SEL_N,
  EP_FM_EJECTOR_LATCH_DETECT_N,
  EP_BMC_RESET,
  EP_FM_SMI_BMC_N,
  EP_PLTRST_N,
  EP_TMP_ALERT,
  EP_RST_I2C_MUX_N,
  EP_XDP_BIC_TRST,
  EP_SMB_BMC_ALERT_N,
  EP_FM_CPLD_BIC_M3_HB,
  EP_IRQ_MEM_SOC_VRHOT_N,
  EP_FM_CRASH_DUMP_V8_N,
  EP_FM_M3_ERR_N,
  EP_FM_CPU_CATERR_LVT3_N,
  EP_BMC_READY_N,
  EP_BMC_COM_SW_N,
  EP_BMC_HB_LED_N,
  EP_FM_VR_FAULT_N,
  EP_IRQ_CPLD_BIC_PROCHOT_N,
  EP_FM_SMB_VR_SOC_MUX_EN,
};
size_t ep_gpio_pin_cnt = sizeof(ep_gpio_pin_list)/sizeof(uint8_t);


// TL GPIO name
const char *gpio_pin_name[] = {
  "PWRGD_COREPWR",
  "PWRGD_PCH_PWROK",
  "PVDDR_AB_VRHOT_N",
  "PVDDR_DE_VRHOT_N",
  "PVCCIN_VRHOT_N",
  "FM_THROTTLE_N",
  "FM_PCH_BMC_THERMTRIP_N",
  "H_MEMHOT_CO_N",
  "FM_CPU0_THERMTRIP_LVT3_N",
  "CPLD_PCH_THERMTRIP",
  "FM_CPLD_FIVR_FAULT",
  "FM_CPU_CATERR_N",
  "FM_CPU_ERROR_2",
  "FM_CPU_ERROR_1",
  "FM_CPU_ERROR_0",
  "FM_SLPS4_N",
  "FM_NMI_EVENT_BMC_N",
  "FM_SMI_BMC_N",
  "PLTRST_N",
  "FP_RST_BTN_N",
  "RST_BTN_BMC_OUT_N",
  "FM_BIOS_POST_COMPT_N",
  "FM_SLPS3_N",
  "PWRGD_PVCCIN",
  "FM_BACKUP_BIOS_SEL_N",
  "FM_EJECTOR_LATCH_DETECT_N",
  "BMC_RESET",
  "FM_JTAG_BIC_TCK_MUX_SEL_N",
  "BMC_READY_N",
  "BMC_COM_SW_N",
  "RST_I2C_MUX_N",
  "XDP_BIC_PREQ_N",
  "XDP_BIC_TRST",
  "FM_SYS_THROTTLE_LVC3",
  "XDP_BIC_PRDY_N",
  "XDP_PRSNT_IN_N",
  "XDP_PRSNT_OUT_N",
  "XDP_BIC_PWR_DEBUG_N",
  "FM_BIC_JTAG_SEL_N",
};

// RC GPIO name
const char *rc_gpio_pin_name[] = {
  "RC_PWRGD_SYS_PWROK",
  "RC_QDF_PS_HOLD_OUT",
  "RC_PVDDQ_510_VRHOT_N_R1",
  "RC_PVDDQ_423_VRHOT_N_R1",
  "RC_VR_I2C_SEL",
  "RC_QDF_THROTTLE_3P3_N",
  "RC_QDF_FORCE_PMIN",
  "RC_QDF_FORCE_PSTATE",
  "RC_QDF_TEMPTRIP_N",
  "RC_FAST_THROTTLE_N",
  "RC_QDF_LIGHT_THROTTLE_3P3_N",
  "RC_UEFI_DB_MODE_N",
  "RC_QDF_RAS_ERROR_2",
  "RC_QDF_RAS_ERROR_1",
  "RC_QDF_RAS_ERROR_0",
  "RC_SPI_MUX_SEL",
  "RC_QDF_NMI",
  "RC_QDF_SMI",
  "RC_QDF_RES_OUT_N_R",
  "RC_SYS_BUF_RST_N",
  "RC_SYS_BIC_RST_N",
  "RC_FM_BIOS_POST_CMPLT_N",
  "RC_IMC_RDY",
  "RC_PWRGD_PS_PWROK",
  "RC_FM_BACKUP_BIOS_SEL_N",
  "RC_T32_JTAG_DET",
  "RC_BB_BMC_RST_N",
  "RC_QDF_PRSNT_0_N",
  "RC_QDF_PRSNT_1_N",
  "RC_EJCT_DET_N",
  "RC_M2_I2C_MUX_RST_N",
  "RC_BIC_REMOTE_SRST_N",
  "RC_BIC_DB_TRST_N",
  "RC_IMC_BOOT_ERROR",
  "RC_BIC_RDY",
  "RC_QDF_PROCHOT_N",
  "RC_PWR_BIC_BTN_N",
  "RC_PWR_BTN_BUF_N",
  "RC_PMF_REBOOT_REQ_N",
  "RC_BIC_BB_I2C_ALERT",
};

// EP GPIO name
const char *ep_gpio_pin_name[] = {
  "EP_PWRGD_COREPWR",
  "EP_PWRGD_SYS_PWROK",
  "EP_PWRGD_PS_PWROK_PLD",
  "EP_PVCCIN_VRHOT_N",
  "EP_H_MEMHOT_CO_N",
  "EP_FM_CPLD_BIC_THERMTRIP_N",
  "EP_FM_CPU_ERROR_2",
  "EP_FM_CPU_ERROR_1",
  "EP_FM_CPU_ERROR_0",
  "EP_FM_NMI_EVENT_BMC_N",
  "EP_FM_CRASH_DUMP_M3_N",
  "EP_FP_RST_BTN_N",
  "EP_FP_RST_BTN_OUT_N",
  "EP_FM_BIOS_POST_COMPT_N",
  "EP_FM_BACKUP_BIOS_SEL_N",
  "EP_FM_EJECTOR_LATCH_DETECT_N",
  "EP_BMC_RESET",
  "EP_FM_SMI_BMC_N",
  "EP_PLTRST_N",
  "EP_TMP_ALERT",
  "EP_RST_I2C_MUX_N",
  "EP_XDP_BIC_TRST",
  "EP_SMB_BMC_ALERT_N",
  "EP_FM_CPLD_BIC_M3_HB",
  "EP_IRQ_MEM_SOC_VRHOT_N",
  "EP_FM_CRASH_DUMP_V8_N",
  "EP_FM_M3_ERR_N",
  "EP_FM_CPU_CATERR_LVT3_N",
  "EP_BMC_READY_N",
  "EP_BMC_COM_SW_N",
  "EP_BMC_HB_LED_N",
  "EP_FM_VR_FAULT_N",
  "EP_IRQ_CPLD_BIC_PROCHOT_N",
  "EP_FM_SMB_VR_SOC_MUX_EN",
};

int
fby2_get_gpio_name(uint8_t fru, uint8_t gpio, char *name) {

  //TODO: Add support for BMC GPIO pins
  if (fru < 1 || fru > 4) {
#ifdef DEBUG
    syslog(LOG_WARNING, "fby2_get_gpio_name: Wrong fru %u", fru);
#endif
    return -1;
  }

  if (gpio < 0 || gpio > MAX_GPIO_PINS) {
#ifdef DEBUG
    syslog(LOG_WARNING, "fby2_get_gpio_name: Wrong gpio pin %u", gpio);
#endif
    return -1;
  }

  sprintf(name, "%s", gpio_pin_name[gpio]);
  return 0;
}
