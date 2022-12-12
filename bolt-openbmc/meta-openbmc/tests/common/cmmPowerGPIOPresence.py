from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import sys
import unitTestUtil
import logging
import subprocess


def componentPowerPresence():
    """
    Checks that the gpios are correctly showing presence of power
    """
    logger.debug("checking value of gpio PSU presence")
    success = True
    for i in range(1,5):
        cmd = 'cat /tmp/gpionames/PSU' + str(i) + '_PRESENT/value'
        f = subprocess.Popen(cmd,
                             shell=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        info, err = f.communicate()
        info = info.decode('utf-8')
        if len(err) > 0:
            raise Exception(err + " [FAILED]")
        logger.debug("checking value of gpio: PSU" + str(i) + "_PRESENT")
        if '0' not in info:
            success = False

    if success:
        print("component gpio power presence [PASSED]")
        sys.exit(0)
    else:
        print("component gpio power presence [FAILED]")
        sys.exit(1)


if __name__ == "__main__":
    """
    Input to this file should look like the following:
    python cmmPowerGPIOPresenceTest.py
    """
    util = unitTestUtil.UnitTestUtil()
    logger = util.logger(logging.WARN)
    try:
        args = util.Argparser(['--verbose'], [None],
                              ['output all steps from test with mode options: DEBUG, INFO, WARNING, ERROR'])
        if args.verbose is not None:
            logger = util.logger(args.verbose)
        componentPowerPresence()
    except Exception as e:
        print("Component power presence Test [FAILED]")
        print("Error: " + str(e))
        sys.exit(1)
