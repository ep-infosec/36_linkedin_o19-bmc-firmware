#!/usr/bin/env python3
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
import json
import os.path
import fsc_expr
import time
import sys
import signal
import traceback

from fsc_util import Logger, clamp
from fsc_profile import profile_constructor, Sensor
from fsc_zone import Zone, Fan
from fsc_bmcmachine import BMCMachine
from fsc_board import board_fan_actions, board_host_actions, board_callout

RAMFS_CONFIG = '/etc/fsc-config.json'
CONFIG_DIR = '/etc/fsc'
# Enable the following for testing only
#RAMFS_CONFIG = '/tmp/fsc-config.json'
#CONFIG_DIR = '/tmp'
DEFAULT_INIT_BOOST = 100
DEFAULT_INIT_TRANSITIONAL = 70


class Fscd(object):

    DEFAULT_BOOST = 100
    DEFAULT_BOOST_TYPE = 'default'
    DEFAULT_TRANSITIONAL = 70
    DEFAULT_RAMP_RATE = 10

    def __init__(self, config=RAMFS_CONFIG, zone_config=CONFIG_DIR,
                 log_level='warning'):
        Logger.start("fscd", log_level)
        Logger.info("Starting fscd")
        self.zone_config = zone_config
        self.fsc_config = self.get_fsc_config(config)  # json dump from config
        self.boost = self.DEFAULT_BOOST
        self.boost_type = self.DEFAULT_BOOST_TYPE
        self.transitional = self.DEFAULT_TRANSITIONAL
        self.ramp_rate = self.DEFAULT_RAMP_RATE
        self.sensor_fail = None
        self.ssd_progressive_algorithm = None
        self.sensor_valid_check = None
        self.fail_sensor_type = None
        self.fan_dead_boost = None
        self.fan_fail = None

    # TODO: Add checks for invalid config file path
    def get_fsc_config(self, fsc_config):
        if os.path.isfile(fsc_config):
            Logger.info("Started, reading configuration from %s" %
                        (fsc_config))
            with open(fsc_config, 'r') as f:
                return json.load(f)

    def get_config_params(self):
        self.transitional = self.fsc_config['pwm_transition_value']
        self.boost = self.fsc_config['pwm_boost_value']
        if 'boost' in self.fsc_config and 'fan_fail' in self.fsc_config['boost']:
                self.fan_fail = self.fsc_config['boost']['fan_fail']
        if 'boost' in self.fsc_config and 'progressive' in self.fsc_config['boost']:
                if self.fsc_config['boost']['progressive']:
                    self.boost_type = 'progressive'
        if 'fan_dead_boost' in self.fsc_config:
            self.fan_dead_boost = self.fsc_config['fan_dead_boost']
            self.all_fan_fail_counter = 0
        if 'boost' in self.fsc_config and 'sensor_fail' in self.fsc_config['boost']:
                self.sensor_fail = self.fsc_config['boost']['sensor_fail']
                if self.sensor_fail:
                    if 'fail_sensor_type' in self.fsc_config:
                        self.fail_sensor_type = self.fsc_config['fail_sensor_type']
                    if 'ssd_progressive_algorithm' in self.fsc_config:
                        self.ssd_progressive_algorithm = self.fsc_config['ssd_progressive_algorithm']
        if 'sensor_valid_check' in self.fsc_config:
            self.sensor_valid_check = self.fsc_config['sensor_valid_check']
        self.watchdog = self.fsc_config['watchdog']
        if 'fanpower' in self.fsc_config:
            self.fanpower = self.fsc_config['fanpower']
        else:
            self.fanpower = False
        if 'chassis_intrusion' in self.fsc_config:
            self.chassis_intrusion = self.fsc_config['chassis_intrusion']
        else:
            self.chassis_intrusion = False
        if 'ramp_rate' in self.fsc_config:
            self.ramp_rate = self.fsc_config['ramp_rate']
        self.wdfile = None
        if self.watchdog:
            Logger.info("watchdog pinging enabled")
            self.wdfile = open('/dev/watchdog', 'wb+', buffering=0)
            if not self.wdfile:
                Logger.error("couldn't open watchdog device")
            else:
                self.wdfile.write(b'V')
                self.wdfile.flush()
        self.interval = self.fsc_config['sample_interval_ms'] / 1000.0

    def build_profiles(self):
        self.sensors = {}
        self.profiles = {}

        for name, pdata in list(self.fsc_config['profiles'].items()):
            self.sensors[name] = Sensor(name, pdata)
            self.profiles[name] = profile_constructor(pdata)

    def build_fans(self):
        self.fans = {}
        for name, pdata in list(self.fsc_config['fans'].items()):
            self.fans[name] = Fan(name, pdata)

    def build_zones(self):
        self.zones = []
        counter = 0
        for name, data in list(self.fsc_config['zones'].items()):
            filename = data['expr_file']
            with open(os.path.join(self.zone_config, filename), 'r') as exf:
                source = exf.read()
                Logger.info("Compiling FSC expression for zone:")
                Logger.info(source)
                (expr, inf) = fsc_expr.make_eval_tree(source,
                                                      self.profiles)
                for name in inf['ext_vars']:
                    board, sname = name.split(':')
                    self.machine.frus.add(board)

                zone = Zone(data['pwm_output'], expr, inf, self.transitional,
                            counter, self.boost, self.sensor_fail, self.sensor_valid_check, self.fail_sensor_type,
                            self.ssd_progressive_algorithm)
                counter += 1
                self.zones.append(zone)

    def build_machine(self):
        self.machine = BMCMachine()

    def fsc_fan_action(self, fan, action):
        '''
        Method invokes board actions for a fan.
        '''
        if 'dead' in action:
            board_fan_actions(fan, action='dead')
            board_fan_actions(fan, action='led_red')
        if 'recover' in action:
            board_fan_actions(fan, action='recover')
            board_fan_actions(fan, action='led_blue')

    def fsc_host_action(self, action, cause):
        if 'host_shutdown' in action:
            board_host_actions(action='host_shutdown', cause=cause)
            #board_fan_actions(fan, action='led_blue')

    def fsc_set_all_fan_led(self, color):
        for fan, _value in list(self.fans.items()):
            board_fan_actions(self.fans[fan], action=color)

    def fsc_safe_guards(self, sensors_tuples):
        '''
        Method defines safe guards for fsc.
        Examples: Triggers board action when sensor temp read reaches limits
        configured in json
        '''
        for fru in self.machine.frus:
            for sensor, tuple in list(sensors_tuples[fru].items()):
                if tuple.name in self.fsc_config['profiles']:
                    if 'read_limit' in self.fsc_config['profiles'][tuple.name]:
                        # If temperature read exceeds accpetable temperature reading
                        if 'valid' in self.fsc_config['profiles'][tuple.name]['read_limit']:
                            valid_table = self.fsc_config['profiles'][tuple.name]['read_limit']['valid']
                            valid_read_limit = valid_table['limit']
                            valid_read_action = valid_table['action']
                            if tuple.value > valid_read_limit:
                                reason = sensor + '(v=' + str(tuple.value) + \
                                    ') limit(t=' + str(valid_read_limit) + \
                                    ') reached'
                                self.fsc_host_action(action=valid_read_action,
                                                     cause=reason)
                        # If temperature read fails
                        if 'invalid' in self.fsc_config['profiles'][tuple.name]['read_limit']:
                            invalid_table = self.fsc_config['profiles'][tuple.name]['read_limit']['invalid']
                            invalid_read_th = invalid_table['threshold']
                            invalid_read_action = invalid_table['action']
                            if tuple.read_fail_counter >= invalid_read_th:
                                reason = sensor + '(value=' + str(tuple.value) + \
                                        ') failed to read ' + \
                                        str(tuple.read_fail_counter) + ' times'
                                self.fsc_host_action(action=invalid_read_action,
                                                     cause=reason)

    def update_dead_fans(self, dead_fans):
        '''
        Check for dead and recovered fans
        '''
        last_dead_fans = dead_fans.copy()
        speeds = self.machine.read_fans(self.fans)
        print("\x1b[2J\x1b[H")
        sys.stdout.flush()

        for fan, rpms in list(speeds.items()):
            Logger.info("%s speed: %d RPM" % (fan.label, rpms))
            if rpms < self.fsc_config['min_rpm']:
                dead_fans.add(fan)
                self.fsc_fan_action(fan, action='dead')
            else:
                dead_fans.discard(fan)

        recovered_fans = last_dead_fans - dead_fans
        newly_dead_fans = dead_fans - last_dead_fans
        if len(newly_dead_fans) > 0:
            if self.fanpower:
                Logger.warn("%d fans failed" % (len(dead_fans),))
            else:
                Logger.crit("%d fans failed" % (len(dead_fans),))
            for dead_fan in dead_fans:
                if self.fanpower:
                    Logger.warn("%s dead, %d RPM" % (dead_fan.label,
                                speeds[dead_fan]))
                else:
                    Logger.crit("%s dead, %d RPM" % (dead_fan.label,
                                speeds[dead_fan]))
                Logger.usbdbg("%s fail" % (dead_fan.label))
        for fan in recovered_fans:
            if self.fanpower:
                Logger.warn("%s has recovered" % (fan.label,))
            else:
                Logger.crit("%s has recovered" % (fan.label,))
            Logger.usbdbg("%s recovered" % (fan.label))
            self.fsc_fan_action(fan, action='recover')
        return dead_fans

    def update_zones(self, dead_fans, time_difference):
        """
            TODO: Need to change logic here.

            # Platforms with chassis_intrusion mode enabled
            if chassis_intrusion:
                set the chassis_intrusion_boost_flag to 0
                and then do necessary checks to set flag to 1
                if chassis_intrusion_boost_flag:
                    run boost mode
                else:
                    run normal mode
            else
                # Platforms WITHOUT chassis_intrusion mode
                run normal mode

        """
        sensors_tuples = self.machine.read_sensors(self.sensors)
        self.fsc_safe_guards(sensors_tuples)
        for zone in self.zones:
            Logger.info("PWM: %s" % (json.dumps(zone.pwm_output)))

            chassis_intrusion_boost_flag = 0
            if self.chassis_intrusion:
                self_tray_pull_out = board_callout(
                    callout='chassis_intrusion')
                if self_tray_pull_out == 1:
                    chassis_intrusion_boost_flag = 1

            if chassis_intrusion_boost_flag == 0:
                pwmval = zone.run(sensors=sensors_tuples, dt=time_difference)
            else:
                pwmval = self.boost

            if self.fan_fail:
                if self.boost_type == 'progressive' and self.fan_dead_boost:
                    # Cases where we want to progressively bump PWMs
                    dead = len(dead_fans)
                    if dead > 0:
                        Logger.info("Progressive mode: Failed fans: %s" %
                              (', '.join([str(i.label) for i in dead_fans],)))
                        for fan_count, rate in self.fan_dead_boost["data"]:
                            if dead <= fan_count:
                                pwmval = clamp(pwmval + (dead * rate), 0, 100)
                                break
                        else:
                            pwmval = self.boost
                else:
                    if dead_fans:
                        # If not progressive ,when there is 1 fan failed, boost all fans
                        Logger.info("Failed fans: %s" % (
                            ', '.join([str(i.label) for i in dead_fans],)))
                        pwmval = self.boost
                    if self.fan_dead_boost:
                        # If all the fans failed take action after a few cycles
                        if len(dead_fans) == len(self.fans):
                            self.all_fan_fail_counter = self.all_fan_fail_counter + 1
                            Logger.warn("Currently all fans failed for {} cycles".format(self.all_fan_fail_counter))
                            if self.fan_dead_boost["threshold"] and self.fan_dead_boost["action"]:
                                if self.all_fan_fail_counter >= self.fan_dead_boost["threshold"]:
                                    self.fsc_host_action(
                                        action=self.fan_dead_boost["action"],
                                        cause="All fans are bad for more than "
                                              + str(self.fan_dead_boost["threshold"])
                                              + " cycles"
                                        )
                        else:
                            # If atleast 1 fan is working reset the counter
                            self.all_fan_fail_counter = 0

            if abs(zone.last_pwm - pwmval) > self.ramp_rate:
                if pwmval < zone.last_pwm:
                    pwmval = zone.last_pwm - self.ramp_rate
                else:
                    pwmval = zone.last_pwm + self.ramp_rate
            zone.last_pwm = pwmval

            if hasattr(zone.pwm_output, '__iter__'):
                for output in zone.pwm_output:
                    self.machine.set_pwm(self.fans.get(
                        str(output)), pwmval)
            else:
                self.machine.set_pwm(self.fans[zone.pwm_output], pwmval)

    def builder(self):
        '''
        Method to extract from json and build all internal data staructures
        '''
        # Build a bmc machine object - read/write sensors
        self.build_machine()
        # Extract everything from json
        self.get_config_params()
        self.build_fans()
        self.build_profiles()
        Logger.info("Available profiles: " + ", ".join(list(self.profiles.keys())))
        self.build_zones()
        Logger.info("Read %d zones" % (len(self.zones)))
        Logger.info("Including sensors from: " + ", ".join(self.machine.frus))

    def get_fan_power_status(self):
        '''
        Method invokes board action to determine fan power status.
        If not applicable returns True.
        '''
        if board_callout(callout='read_power'):
            return True
        return False

    def run(self):
        """
        Main FSCD method that builds from the fscd config and runs
        """

        # Get everything from json and build profiles, fans, zones
        self.builder()

        self.machine.set_all_pwm(self.fans, self.transitional)
        self.fsc_set_all_fan_led(color='led_blue')

        last = time.time()
        dead_fans = set()

        if self.fanpower:
            time.sleep(30)

        while True:
            if self.wdfile:
                self.wdfile.write(b'V')
                self.wdfile.flush()

            time.sleep(self.interval)

            if self.fanpower:
                if not self.get_fan_power_status():
                    continue
            if self.fan_fail:
                # Get dead fans for determining speed
                dead_fans = self.update_dead_fans(dead_fans)

            now = time.time()
            time_difference = now - last
            last = now

            # Check sensors and update zones
            self.update_zones(dead_fans, time_difference)


def handle_term(signum, frame):
    global wdfile
    board_callout(callout='init_fans', boost=DEFAULT_INIT_TRANSITIONAL)
    Logger.warn("killed by signal %d" % (signum,))
    if signum == signal.SIGQUIT and wdfile:
        Logger.info("Killed with SIGQUIT - stopping watchdog.")
        wdfile.write(b"X")
        wdfile.flush()
        wdfile.close()
        wdfile = None
    sys.exit('killed')


if __name__ == "__main__":
    try:
        signal.signal(signal.SIGTERM, handle_term)
        signal.signal(signal.SIGINT, handle_term)
        signal.signal(signal.SIGQUIT, handle_term)
        if len(sys.argv) > 1:
            llevel = sys.argv[1]
        else:
            llevel = 'warning'
        fscd = Fscd(log_level=llevel)
        fscd.run()
    except Exception:
        board_callout(callout='init_fans', boost=DEFAULT_INIT_TRANSITIONAL)
        (etype, e) = sys.exc_info()[:2]
        Logger.crit("failed, exception: " + str(etype))
        traceback.print_exc()
        for line in traceback.format_exc().split('\n'):
            Logger.crit(line)
