#!/bin/sh
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

### BEGIN INIT INFO
# Provides:          setup-consoled
# Required-Start:
# Required-Stop:
# Default-Start:     S
# Default-Stop:
# Short-Description: Setup console history buffering
### END INIT INFO

. /usr/local/fbpackages/utils/ast-functions

# TODO: check for the if slot/server is present before starting the daemon
echo -n "Setup console  buffering..."

  if [ $(is_server_prsnt 1) == "1" ] ; then
    /usr/local/bin/consoled slot1 --buffer
  fi

  if [ $(is_server_prsnt 2) == "1" ] ; then
    /usr/local/bin/consoled slot2 --buffer
  fi

  if [ $(is_server_prsnt 3) == "1" ] ; then
    /usr/local/bin/consoled slot3 --buffer
  fi

  if [ $(is_server_prsnt 4) == "1" ] ; then
    /usr/local/bin/consoled slot4 --buffer
  fi

echo "done."
