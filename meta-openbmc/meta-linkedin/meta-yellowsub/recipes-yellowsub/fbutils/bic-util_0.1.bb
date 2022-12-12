# Copyright 2015-present Facebook. All Rights Reserved.
SUMMARY = "Bridge IC Utility"
DESCRIPTION = "Util for checking with Bridge IC on Yellowsub"
SECTION = "base"
PR = "r1"
LICENSE = "GPLv2"
LIC_FILES_CHKSUM = "file://bic-util.c;beginline=4;endline=16;md5=b395943ba8a0717a83e62ca123a8d238"

SRC_URI = "file://bic-util \
          "

S = "${WORKDIR}/bic-util"

CFLAGS += " -lbic -lipmi -lipmb -lbic -lyellowsub_gpio "


do_install() {
	  install -d ${D}${bindir}
    install -m 0755 bic-util ${D}${bindir}/bic-util
}

DEPENDS += "libbic libipmi libipmb libyellowsub-gpio"
RDEPENDS_${PN} += "libbic libipmi libipmb libyellowsub-gpio"

FILES_${PN} = "${bindir}"
