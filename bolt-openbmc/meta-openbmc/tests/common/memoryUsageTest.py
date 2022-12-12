from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import sys
import subprocess
import unitTestUtil
import logging


def memory_usage_check(threshold):
    """
    Check to make sure all forms of memory usage are below a given threshold
    """
    logger.debug("executing command: free")
    f = subprocess.Popen('free',
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    info, err = f.communicate()
    if len(err) != 0:
        raise Exception(err)
    info = info.decode('utf-8')
    info = info.split('\n')
    line = info[1].split(" ")
    line = list(filter(lambda x: x != '', line))
    used = int(100 - (float(line[3]) / float(line[1])) * 100)
    if used < threshold:
        print("Memory usage is below threshold: " + str(threshold) +
              "% [PASSED]")
        sys.exit(0)
    else:
        print(
            str(used) +
            "% of memory has been used which is greater than the threshold of "
            + str(threshold) + "% [FAILED]")
        sys.exit(1)


if __name__ == "__main__":
    """
    Input to this file should look like the following:
    python memoryUsageTest.py 90
    """
    util = unitTestUtil.UnitTestUtil()
    logger = util.logger(logging.WARN)
    try:
        args = util.Argparser(['threshold', '--verbose'], [int, None],
                              ['a memory usage percent threshold',
                              'output all steps from test with mode options: DEBUG, INFO, WARNING, ERROR'])
        if args.verbose is not None:
            logger = util.logger(args.verbose)
        memory_usage_check(args.threshold)
    except Exception as e:
        print("memory usage test [FAILED]")
        print("Error code returned: " + str(e))
    sys.exit(1)
