# Copyright 2014-present Facebook. All Rights Reserved.
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
SUMMARY = "Utilities"
DESCRIPTION = "Various utilities"
SECTION = "base"
PR = "r1"
LICENSE = "GPLv2"
LIC_FILES_CHKSUM = "file://COPYING;md5=eb723b61539feef013de476e68b5c50a"

SRC_URI = "file://ast-functions \
           file://sol-util \
           file://power_led.sh \
           file://setup-gpio.sh \
           file://power-on.sh \
           file://eth0_mac_fixup.sh \
           file://sync_date.sh \
           file://setup-snoopdma.sh \
           file://setup-por.sh \
           file://COPYING \
          "

pkgdir = "utils"

S = "${WORKDIR}"

binfiles = "power_led.sh sync_date.sh sol-util \
  "

DEPENDS_append = "update-rc.d-native"

do_install() {
  dst="${D}/usr/local/fbpackages/${pkgdir}"
  install -d $dst
  install -m 644 ast-functions ${dst}/ast-functions
  localbindir="${D}/usr/local/bin"
  install -d ${localbindir}
  for f in ${binfiles}; do
      install -m 755 $f ${dst}/${f}
      ln -s ../fbpackages/${pkgdir}/${f} ${localbindir}/${f}
  done

  # init
  install -d ${D}${sysconfdir}/init.d
  install -d ${D}${sysconfdir}/rcS.d
  # the script to mount /mnt/data
  install -m 755 setup-gpio.sh ${D}${sysconfdir}/init.d/setup-gpio.sh
  update-rc.d -r ${D} setup-gpio.sh start 59 5 .
  # networking is done after rcS, any start level within rcS
  # for mac fixup should work
  install -m 755 eth0_mac_fixup.sh ${D}${sysconfdir}/init.d/eth0_mac_fixup.sh
  update-rc.d -r ${D} eth0_mac_fixup.sh start 70 S .
  install -m 755 setup-snoopdma.sh ${D}${sysconfdir}/init.d/setup-snoopdma.sh
  update-rc.d -r ${D} setup-snoopdma.sh start 82 S .
  install -m 755 power-on.sh ${D}${sysconfdir}/init.d/power-on.sh
  update-rc.d -r ${D} power-on.sh start 96 5 .
  install -m 755 sync_date.sh ${D}${sysconfdir}/init.d/sync_date.sh
  update-rc.d -r ${D} sync_date.sh start 66 5 .
  install -m 755 setup-por.sh ${D}${sysconfdir}/init.d/setup-por.sh
  update-rc.d -r ${D} setup-por.sh start 70 S .
}

FILES_${PN} += "/usr/local ${sysconfdir}"

RDEPENDS_${PN} = "bash"
