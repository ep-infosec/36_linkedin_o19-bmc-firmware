# Copyright 2015-present Facebook. All Rights Reserved.
SUMMARY = "Yosemite Sensor Library"
DESCRIPTION = "library for reading various sensors"
SECTION = "base"
PR = "r1"
LICENSE = "GPLv2"
LIC_FILES_CHKSUM = "file://yosemite_sensor.c;beginline=8;endline=20;md5=da35978751a9d71b73679307c4d296ec"


SRC_URI = "file://yosemite_sensor \
          "
DEPENDS =+ " libipmi libipmb libbic libyosemite-common obmc-i2c obmc-pal "

S = "${WORKDIR}/yosemite_sensor"

do_install() {
	  install -d ${D}${libdir}
    install -m 0644 libyosemite_sensor.so ${D}${libdir}/libyosemite_sensor.so

    install -d ${D}${includedir}/facebook
    install -m 0644 yosemite_sensor.h ${D}${includedir}/facebook/yosemite_sensor.h
}

FILES_${PN} = "${libdir}/libyosemite_sensor.so"
FILES_${PN}-dev = "${includedir}/facebook/yosemite_sensor.h"
