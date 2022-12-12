from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import sys
import os
import re
try:
    currentPath = os.getcwd()
    commonPath = currentPath.replace('fbttn/unittests', 'common')
    sys.path.insert(0, commonPath)
except Exception:
    pass
import BaseUtil


class FbttnUtil(BaseUtil.BaseUtil):

    # Sensors
    SensorCmd = '/usr/local/bin/sensor-util all'

    # Fans
    GetFanCmd = '/usr/local/bin/fan-util --get 0'
    SetFanCmd = '/usr/local/bin/fan-util --set 0'
    KillControlCmd = ['/usr/bin/sv stop fscd']
    StartControlCmd = '/usr/bin/sv start fscd'

    def get_speed(self, info):
        """
        Supports getting fan pwm for Tioga Pass
        """
        info = info.decode('utf-8')
        info = info.split(':')[1].split('RPM')
        pwm_str = re.sub("[^0-9]", "", info[1])
        return int(pwm_str)

    def get_fan_test(self, info):
        info = info.decode('utf-8')
        info = info.split('\n')
        goodRead = ['Fan', 'RPM', '%', 'Speed']
        for line in info:
            if len(line) == 0:
                continue
            for word in goodRead:
                if word not in line:
                    return False
        return True

    # EEPROM
    ProductName = ['BryceCanyon']
    EEPROMCmd = '/usr/local/bin/fruid-util iom'

    # Power Cycle
    PowerCmdOn = '/usr/local/bin/power-util server on'
    PowerCmdOff = '/usr/local/bin/power-util server off'
    PowerCmdReset = '/usr/local/bin/power-util server reset'
    PowerCmdStatus = '/usr/local/bin/power-util server status'
    PowerHW = '/usr/local/bin/power-util mb status && echo "on" || echo "off"'

    # sol
    solCmd = '/usr/local/bin/sol-util server'
    solCloseConnection = ['\r', 'CTRL-l', 'x']

    def solConnectionClosed(self, info):
        if 'Connection closed' in info:
            return True
        else:
            return False

    daemonProcessesKill = ['/usr/bin/sv stop fscd', '/usr/bin/sv stop healthd']
