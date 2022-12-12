#!/usr/bin/env python
import sys
import re
import os.path
import argparse
import json
from subprocess import Popen, PIPE
from ctypes import *
from bios_boot_order import *
from bios_postcode import *
from bios_plat_info import *
from bios_pcie_port_config import *


BIOS_UTIL_CONFIG = '/usr/local/fbpackages/bios-util/bios_support.json'
BIOS_UTIL_DEFAULT_CONFIG = '/usr/local/fbpackages/bios-util/bios_default_support.json'
supported_commands = ["--boot_order", "--postcode", "--plat_info", "--pcie_port_config"]

def bios_main_fru(fru, command):
    if ( command == "--boot_order" ):
        boot_order(fru, sys.argv[1:])
    elif ( command == "--postcode" ):
        postcode(fru, POST_CODE_FILE)
    elif ( command == "--plat_info" ):
        plat_info(fru)
    elif ( command == "--pcie_port_config" ):   
        pcie_port_config(fru, sys.argv[1:])

class check_bios_util(object):
    def __init__(self, config=BIOS_UTIL_CONFIG, default_config=BIOS_UTIL_DEFAULT_CONFIG, argv=sys.argv):
        self.argv = argv
        # json dump from config
        self.bios_support_config = self.get_bios_support_config(config)
        if self.bios_support_config == "NULL":
            print("Use default supported config.")
            self.bios_support_config = self.get_bios_support_config(default_config)
            if self.bios_support_config == "NULL":
                print("No JSON config can be used. Exit bios-util.")
                self.valid = False
                return None

        self.get_config_params()
        self.valid = self.show_bios_util_usage()

    def show_bios_util_usage(self):
        # parse bios-util usage
        parser = argparse.ArgumentParser(description='Show bios-util usage')
        parser.add_argument("FRU", nargs=1, help='FRU name')
        if self.bios_util_action == "true":
            group = parser.add_mutually_exclusive_group()

        # According to json config to select which feature is supported
        self.boot_order_message = "["
        boot_order_actions = 0
        if self.boot_mode:
            self.boot_order_message = self.boot_order_message  + "--boot_mode"
            boot_order_actions = boot_order_actions + 1
        if self.clear_cmos:
            if boot_order_actions != 0:
                self.boot_order_message = self.boot_order_message  + " | --clear_CMOS"
            else:
                self.boot_order_message = self.boot_order_message  + "--clear_CMOS"
            boot_order_actions = boot_order_actions + 1
        if self.force_boot_bios_setup:
            if boot_order_actions != 0:
                self.boot_order_message = self.boot_order_message  + " | --force_boot_BIOS_setup"
            else:
                self.boot_order_message = self.boot_order_message  + "--force_boot_BIOS_setup"
            boot_order_actions = boot_order_actions + 1
        if self.boot_order:
            if boot_order_actions != 0:
                self.boot_order_message = self.boot_order_message  + " | --boot_order"
            else:
                self.boot_order_message = self.boot_order_message  + "--boot_order"
            boot_order_actions = boot_order_actions + 1

        self.boot_order_message = self.boot_order_message + "]"

        if self.clear_cmos or self.force_boot_bios_setup:
            if self.boot_mode or self.boot_order:
                group.add_argument("--boot_order", dest="command", action="store", choices=["enable", "disable", "set", "get"], help="Enable or disable or set or get BIOS boot order")
            else:
                group.add_argument("--boot_order", dest="command", action="store", choices=["enable", "disable", "get"], help="Enable or disable or get BIOS boot order")
        else:
            if self.boot_mode or self.boot_order:
                group.add_argument("--boot_order", dest="command", action="store", choices=["set", "get"], help="Set or get BIOS boot order")

        if self.postcode:
            group.add_argument("--postcode", dest="command", action="store", choices=["get"], help="Get POST code")
        if self.plat_info:
            group.add_argument("--plat_info", dest="command", action="store", choices=["get"], help="Get platform information")
        if self.pcie_port_config:
            group.add_argument("--pcie_port_config", dest="command", action="store", choices=["enable", "disable", "get"], help="Enable or disable or get PCIe port configuration")

        if len(self.argv) > 1 and len(self.argv) == 3:
            args = parser.parse_args(self.argv[1:3])
        elif len(self.argv) >= 4:
            args = parser.parse_args(self.argv[1:4])
        else:
            parser.print_help()
            return False

        self.bios_usage_message = "bios-util " + str(self.argv[1]) + " " + str(self.argv[2]) + " " + str(self.argv[3])
        if hasattr(self, args.command):
            return getattr(self, args.command)()
        else:
            parser.print_help()
            return False

    def get_bios_support_config(self, bios_support_config):
        config = "NULL"
        if os.path.isfile(bios_support_config):
            with open(bios_support_config, 'r') as f:
                config = json.load(f)
        else:
            print(bios_support_config + " is missing!")

        return config

    def get_config_params(self):
        self.bios_util_action = "false"
        if 'boot_mode' in self.bios_support_config and 'supported' in self.bios_support_config['boot_mode']:
            self.boot_mode = self.bios_support_config['boot_mode']['supported']
        if 'clear_cmos' in self.bios_support_config and 'supported' in self.bios_support_config['clear_cmos']:
            self.clear_cmos = self.bios_support_config['clear_cmos']['supported']
        if 'force_boot_bios_setup' in self.bios_support_config and 'supported' in self.bios_support_config['force_boot_bios_setup']:
            self.force_boot_bios_setup = self.bios_support_config['force_boot_bios_setup']['supported']
        if 'boot_order' in self.bios_support_config and 'supported' in self.bios_support_config['boot_order']:
            self.boot_order = self.bios_support_config['boot_order']['supported']
        if 'plat_info' in self.bios_support_config and 'supported' in self.bios_support_config['plat_info']:
            self.plat_info = self.bios_support_config['plat_info']['supported']
        if 'pcie_port_config' in self.bios_support_config and 'supported' in self.bios_support_config['pcie_port_config']:
            self.pcie_port_config = self.bios_support_config['pcie_port_config']['supported']
            self.pcie_ports = self.bios_support_config['pcie_port_config']['pcie_ports']
            self.pcie_port_message = "[--" + self.pcie_ports.replace(', ', ' | --') + "]"
            self.pcie_ports = self.pcie_ports.split(', ')
        if 'postcode' in self.bios_support_config and 'supported' in self.bios_support_config['postcode']:
            self.postcode = self.bios_support_config['postcode']['supported']

        if self.boot_mode or self.clear_cmos or self.force_boot_bios_setup or self.boot_order \
           or self.plat_info or self.pcie_port_config or self.postcode:
           self.bios_util_action = "true"

    def set(self):
        if self.argv[2] == "--boot_order":
            msg_set_option = ""
            if self.boot_mode:
                if self.boot_order:
                    msg_set_option = "[--boot_mode | --boot_order]"
                else:
                    msg_set_option = "[--boot_mode]"
            elif self.boot_order:
                msg_set_option = "[--boot_order]"

            parser = argparse.ArgumentParser(description='Show Set Boot Order usage',
                usage=self.bios_usage_message + " [-h] " + msg_set_option)

            group = parser.add_mutually_exclusive_group()
            if self.boot_mode:
                group.add_argument("--boot_mode", action="store", choices=["0", "1"], help="Set BIOS boot mode {0: 'Legacy', 1: 'UEFI'}")

            if self.boot_order:
                group.add_argument("--boot_order", nargs=5, metavar="order#", help="Set BIOS boot order " + repr(boot_order_device))

            if len(self.argv) < 5:
                parser.print_help()
                return False
            args = parser.parse_args(self.argv[4:])

        return True

    def get(self):
        if self.argv[2] == "--boot_order":
            parser = argparse.ArgumentParser(description='Show Get Boot Order usage',
                usage=self.bios_usage_message + " [-h] " + self.boot_order_message)

            group = parser.add_mutually_exclusive_group()
            if self.boot_mode:
                group.add_argument("--boot_mode", action="store_true", help="Get Boot mode setting")
            if self.clear_cmos:
                group.add_argument("--clear_CMOS", action="store_true", help="Get CMOS clear setting")
            if self.force_boot_bios_setup:
                group.add_argument("--force_boot_BIOS_setup", action="store_true", help="Get Force Boot into BIOS Setup setting")
            if self.boot_order:
                group.add_argument("--boot_order", action="store_true", help="Get BIOS Boot order")

            if len(self.argv) < 5:
                parser.print_help()
                return False
            args = parser.parse_args(self.argv[4:])

            return True

        else:
            parser = argparse.ArgumentParser(description='get',
                usage=self.bios_usage_message)
            args = parser.parse_args(self.argv[4:])

            if len(self.argv) > 4:
                parser.print_help()
                return False

        return True

    def enable(self):
        if self.argv[2] == "--boot_order":
            self.boot_order_message = self.boot_order_message.replace('--boot_mode | ', '')
            self.boot_order_message = self.boot_order_message.replace(' | --boot_order', '')
            parser = argparse.ArgumentParser(description='Show Enable Boot Order usage',
                usage=self.bios_usage_message + " [-h] " + self.boot_order_message)

            group = parser.add_mutually_exclusive_group()
            if self.clear_cmos:
                group.add_argument("--clear_CMOS", action="store_true", help="Enable clear CMOS")
            if self.force_boot_bios_setup:
                group.add_argument("--force_boot_BIOS_setup", action="store_true", help="Enable Force Boot into BIOS Setup")

            if len(self.argv) < 5:
                parser.print_help()
                return False

            args = parser.parse_args(self.argv[4:6])

        elif self.argv[2] == "--pcie_port_config":
            parser = argparse.ArgumentParser(description='Show Enable PCIe Port Configuration usage',
                    usage=self.bios_usage_message + " [-h] " + self.pcie_port_message)

            group = parser.add_mutually_exclusive_group()
            for i in range(0, len(self.pcie_ports), 1):
                group.add_argument("--" + self.pcie_ports[i], action="store_true", help="Enable the PCIe device of " + self.pcie_ports[i])

            if len(self.argv) < 5:
                parser.print_help()
                return False

            args = parser.parse_args(self.argv[4:6])

        return True

    def disable(self):
        if self.argv[2] == "--boot_order":
            self.boot_order_message = self.boot_order_message.replace('--boot_mode | ', '')
            parser = argparse.ArgumentParser(description='Show Disable Boot Order usage',
                usage=self.bios_usage_message + " [-h] " + self.boot_order_message)

            group = parser.add_mutually_exclusive_group()
            if self.clear_cmos:
                group.add_argument("--clear_CMOS", action="store_true", help="Disable clear CMOS")
            if self.force_boot_bios_setup:
                group.add_argument("--force_boot_BIOS_setup", action="store_true", help="Disable Force Boot into BIOS Setup")
            if self.boot_order:
                group.add_argument("--boot_order", action="store_true", help="Disable to set BIOS Boot order")

            if len(self.argv) < 5:
                parser.print_help()
                return False

            args = parser.parse_args(self.argv[4:6])

        elif self.argv[2] == "--pcie_port_config":
            parser = argparse.ArgumentParser(description='Show Disable PCIe Port Configuration usage',
                    usage=self.bios_usage_message + " [-h] " + self.pcie_port_message)

            group = parser.add_mutually_exclusive_group()
            for i in range(0, len(self.pcie_ports), 1):
                group.add_argument("--" + self.pcie_ports[i], action="store_true", help="Disable the PCIe device of " + self.pcie_ports[i])

            if len(self.argv) < 5:
                parser.print_help()
                return False

            args = parser.parse_args(self.argv[4:6])

        return True
