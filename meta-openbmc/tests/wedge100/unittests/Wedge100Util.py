from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import sys
import os
import re
try:
    currentPath = os.getcwd()
    commonPath = currentPath.replace('wedge100/unittests', 'common')
    sys.path.insert(0, commonPath)
except Exception:
    pass
import BaseUtil


class Wedge100Util(BaseUtil.BaseUtil):

    # Sensors
    SensorCmd = '/usr/bin/sensors'

    # Fans
    GetFanCmd = '/usr/local/bin/get_fan_speed.sh 1'
    SetFanCmd = '/usr/local/bin/set_fan_speed.sh 0'
    KillControlCmd = ['/usr/local/bin/watchdog_ctrl.sh off', '/usr/bin/killall -USR1 fand']
    StartControlCmd = 'sh /etc/init.d/setup-fan.sh'

    def get_speed(self, info):
        """
        Supports getting fan pwm for wedge100
        """
        info = info.decode('utf-8')
        info = info.split(':')[1].split(',')
        pwm_str = re.sub("[^0-9]", "", info[2])
        return int(pwm_str)

    def get_fan_test(self, info):
        info = info.decode('utf-8')
        info = info.split('\n')
        goodRead = ['Fan', 'RPMs:', '%']
        for line in info:
            if len(line) == 0:
                continue
            for word in goodRead:
                if word not in line:
                    return False
            val = line.split(':')[1].split(',')
            if len(val) != 3:
                return False
        return True

    # EEPROM
    ProductName = ['Wedge100']
    EEPROMCmd = '/usr/bin/weutil'

    # Power Cycle
    PowerCmdOn = '/usr/local/bin/wedge_power.sh on'
    PowerCmdOff = '/usr/local/bin/wedge_power.sh off'
    PowerCmdReset = '/usr/local/bin/wedge_power.sh reset'
    PowerCmdStatus = '/usr/local/bin/wedge_power.sh status'
    PowerHW = 'source /usr/local/bin/board-utils.sh && wedge_is_us_on && echo "on" || echo "off"'

    # sol
    solCmd = '/usr/local/bin/sol.sh'
    solCloseConnection = ['\r', 'CTRL-l', 'x']

    def solConnectionClosed(self, info):
        if 'Connection closed' in info:
            return True
        else:
            return False

    daemonProcessesKill = ['/usr/bin/killall fand']
