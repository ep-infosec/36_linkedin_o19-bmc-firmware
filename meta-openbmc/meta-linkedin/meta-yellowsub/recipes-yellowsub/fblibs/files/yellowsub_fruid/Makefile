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

lib: libyellowsub_fruid.so

libyellowsub_fruid.so: yellowsub_fruid.c
	$(CC) $(CFLAGS) -fPIC -c -o yellowsub_fruid.o yellowsub_fruid.c
	$(CC) -lyellowsub_common -shared -o libyellowsub_fruid.so yellowsub_fruid.o -lc

.PHONY: clean

clean:
	rm -rf *.o libyellowsub_fruid.so
