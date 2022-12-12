# Copyright 2015-present Facebook. All Rights Reserved.
SUMMARY = "Yosemite Common Library"
DESCRIPTION = "library for common Yosemite information"
SECTION = "base"
PR = "r1"
LICENSE = "GPLv2"
LIC_FILES_CHKSUM = "file://yosemite_common.c;beginline=8;endline=20;md5=da35978751a9d71b73679307c4d296ec"


SRC_URI = "file://yosemite_common \
          "
DEPENDS += "libkv libedb"

S = "${WORKDIR}/yosemite_common"

do_install() {
	  install -d ${D}${libdir}
    install -m 0644 libyosemite_common.so ${D}${libdir}/libyosemite_common.so

    install -d ${D}${includedir}
    
    install -d ${D}${includedir}/facebook
    install -m 0644 yosemite_common.h ${D}${includedir}/facebook/yosemite_common.h
}

FILES_${PN} = "${libdir}/libyosemite_common.so"
FILES_${PN}-dev = "${includedir}/facebook/yosemite_common.h"

RDEPENDS_${PN} += " libkv libedb"
