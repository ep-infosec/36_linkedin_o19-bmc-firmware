# Copyright 2015-present Facebook. All Rights Reserved.
SUMMARY = "Expander Utility"
DESCRIPTION = "Util for communicate with Expander on Triton"
SECTION = "base"
PR = "r1"
LICENSE = "GPLv2"
LIC_FILES_CHKSUM = "file://expander-util.c;beginline=4;endline=16;md5=302e73da84735a7814365fd8ab355e2d"

SRC_URI = "file://expander-util \
          "

S = "${WORKDIR}/expander-util"

do_install() {
    install -d ${D}${bindir}
    install -m 0755 expander-util ${D}${bindir}/expander-util
}

DEPENDS += "libipmb libexp"
RDEPENDS_${PN} += "libipmb libexp"

FILES_${PN} = "${bindir}"
