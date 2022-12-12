from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import sys
import subprocess
import unitTestUtil
import logging


def process_check(data):
    """
    given a json of modules, check that all of the modules exist
    """
    logger.debug("executing command: ps")
    f = subprocess.Popen('ps', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    info, err = f.communicate()
    info = info.decode('utf-8')
    if len(err) != 0:
        raise Exception(err)
    failed = []
    for process in data:
        if process in info:
            continue
        else:
            failed += [str(process)]
    if len(failed) == 0:
        print("All Processes are currently running [PASSED]")
        sys.exit(0)
    else:
        print("Processes: " + str(failed) +
              " aren't currently running [FAILED]")
        sys.exit(1)


if __name__ == "__main__":
    """
    Input to this file should look like the following:
    python processRunningTest.py kernel.json
    """
    util = unitTestUtil.UnitTestUtil()
    logger = util.logger(logging.WARN)
    try:
        data = {}
        args = util.Argparser(['json', '--verbose'], [str, None],
                              ['json file',
                              'output all steps from test with mode options: DEBUG, INFO, WARNING, ERROR'])
        if args.verbose is not None:
            logger = util.logger(args.verbose)
        data = util.JSONparser(args.json)
        process_check(data)
    except Exception as e:
        print("Process test [FAILED]")
        print("Error code returned: " + str(e))
    sys.exit(1)
