/* Copyright 2015-present Facebook. All Rights Reserved.
 *
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

#ifndef __MINILAKETB_FRUID_H__
#define __MINILAKETB_FRUID_H__

#include <facebook/minilaketb_common.h>
#include <facebook/minilaketb_sensor.h>

#define MINILAKETB_FRU_PATH "/tmp/fruid_%s.bin"

#define MFG_MELLANOX 0x19810000
#define MFG_BROADCOM 0x3D110000
#define MFG_UNKNOWN 0xFFFFFFFF

#ifdef __cplusplus
extern "C" {
#endif

uint32_t minilaketb_get_nic_mfgid(void);
int minilaketb_get_fruid_path(uint8_t fru, char *path);
int minilaketb_get_fruid_eeprom_path(uint8_t fru, char *path);
int minilaketb_get_fruid_name(uint8_t fru, char *name);

#ifdef __cplusplus
} // extern "C"
#endif

#endif /* __MINILAKETB_FRUID_H__ */
