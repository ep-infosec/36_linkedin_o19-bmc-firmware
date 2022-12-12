from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import sys
import unitTestUtil
import pxssh
import logging


def solTest(utilUnitTest, utilType, hostname):
    """
    For a given platform test that sol is appropriately coming up
    """
    if utilType.solCmd is None:
        raise Exception("sol start command not implemented")
    if utilType.solCloseConnection is None:
        raise Exception("sol close command not implemented")
    ssh = pxssh.pxssh()
    util.Login(hostname, ssh)
    logger.debug("executing command: " + str(utilType.solCmd))
    ssh.sendline(utilType.solCmd)
    ssh.prompt(timeout=5)
    #  after running the sol connection press enter then close the connection
    for cmd in utilType.solCloseConnection:
        if 'CTRL' in cmd:  # if command is a control character
            ssh.sendcontrol(cmd.replace('CTRL-', ''))
        elif cmd == '\r':  # if enter key is pressed
            ssh.sendline(cmd)
            logger.debug("checking that login is present")
            if len(ssh.before) < 20:  # assert login characters pop up
                print("No sol connection [FAILED]")
        else:
            ssh.sendline(cmd)
        ssh.prompt(timeout=5)
    logger.debug("checking that connection closes properly")
    if utilType.solConnectionClosed(ssh.before):
        print("sol Test [PASSED]")
        sys.exit(0)
    else:
        print("sol command not properly executed [FAILED]")
        sys.exit(1)


if __name__ == "__main__":
    """
    Input to this file should look like the following:
    python solTest.py type hostname
    """
    util = unitTestUtil.UnitTestUtil()
    logger = util.logger(logging.WARN)
    try:
        args = util.Argparser(['type', 'host', '--verbose'], [str, str, None],
                              ['a platform type', 'a hostname',
                              'output all steps from test with mode options: DEBUG, INFO, WARNING, ERROR'])
        if args.verbose is not None:
            logger = util.logger(args.verbose)
        platformType = args.type
        hostname = args.host
        utilType = util.importUtil(platformType)
        solTest(util, utilType, hostname)
    except Exception as e:
        print("sol Test [FAILED]")
        print("Error: " + str(e))
    sys.exit(1)
