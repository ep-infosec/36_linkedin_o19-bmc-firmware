#!/usr/bin/env python
#
# Copyright 2015-present Facebook. All Rights Reserved.
#
# This program file is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
# for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program in a file named COPYING; if not, write to the
# Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301 USA
#
from fsc_util import Logger
from ctypes import *
from subprocess import Popen, PIPE
from re import match

lpal_hndl = CDLL("libpal.so")

fru_map = {
    'slot1': {
        'name': 'fru1',
        'pwr_gpio': '64',
        'bic_ready_gpio': '106',
        'slot_num': 1
    },
    'slot2': {
        'name': 'fru2',
        'pwr_gpio': '65',
        'bic_ready_gpio': '107',
        'slot_num': 2
    },
    'slot3': {
        'name': 'fru3',
        'pwr_gpio': '66',
        'bic_ready_gpio': '108',
        'slot_num': 3
    },
    'slot4': {
        'name': 'fru4',
        'pwr_gpio': '67',
        'bic_ready_gpio': '109',
        'slot_num': 4
    }
}

loc_map = {
    'a0': "_dimm0_location",
    'a1': "_dimm1_location",
    'b0': "_dimm2_location",
    'b1': "_dimm3_location",
    'd0': "_dimm4_location",
    'd1': "_dimm5_location",
    'e0': "_dimm6_location",
    'e1': "_dimm7_location"
}

def board_fan_actions(fan, action='None'):
    '''
    Override the method to define fan specific actions like:
    - handling dead fan
    - handling fan led
    '''
    if action in 'dead':
        # TODO: Why not do return pal_fan_dead_handle(fan)
        lpal_hndl.pal_fan_dead_handle(fan.fan_num)
    elif action in 'recover':
        # TODO: Why not do return pal_fan_recovered_handle(fan)
        lpal_hndl.pal_fan_recovered_handle(fan.fan_num)
    elif "led" in action:
        # No Action Needed. LED controlled in action 'dead' and 'recover'.
        pass
    else:
        Logger.warn("%s needs action %s" % (fan.label, str(action),))
    pass


def board_host_actions(action='None', cause='None'):
    '''
    Override the method to define fan specific actions like:
    - handling host power off
    - alarming/syslogging criticals
    '''
    pass


def board_callout(callout='None', **kwargs):
    '''
    Override this method for defining board specific callouts:
    - Exmaple chassis intrusion
    '''
    if 'init_fans' in callout:
        boost = 100 # define a boost for the platform or respect fscd override
        if 'boost' in kwargs:
            boost = kwargs['boost']
        return set_all_pwm(boost)
    else:
        Logger.warning("Callout %s not handled" % callout)
    pass


def set_all_pwm(boost):
    cmd = ('/usr/local/bin/fan-util --set %d' % (boost))
    response = Popen(cmd, shell=True, stdout=PIPE).stdout.read()
    response = response.decode()
    return response

def sensor_valid_check(board, sname, check_name, attribute):
    try:
        if attribute['type'] == "power_status":
            with open("/sys/class/gpio/gpio"+fru_map[board]['pwr_gpio']+"/value", "r") as f:
                pwr_sts = f.read(1)
            if pwr_sts[0] == "1":
                slot_id = fru_map[board]['slot_num']
                is_slot_server = lpal_hndl.pal_is_slot_server(slot_id)
                if int(is_slot_server) == 1:
                    with open("/sys/class/gpio/gpio"+fru_map[board]['bic_ready_gpio']+"/value", "r") as f:
                        bic_sts = f.read(1)
                    if bic_sts[0] == "0":
                        if match(r'soc_dimm', sname) != None:
                            # check DIMM present
                            with open("/mnt/data/kv_store/sys_config/"+fru_map[board]['name']+loc_map[sname[8:10]], "rb") as f:
                                dimm_sts = f.read(1)
                            if dimm_sts[0] != 1:
                                return 0
                        return 1
                else:
                    return 1    
            return 0
        else:
            Logger.debug("Sensor corresponding valid check funciton not found!")
            return 0
    except SystemExit:
        Logger.debug("SystemExit from sensor read")
        raise
    except Exception:
        Logger.warn("Exception with board=%s, sensor_name=%s" % (board, sname))
    return 0
