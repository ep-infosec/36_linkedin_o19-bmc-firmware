SUMMARY = "ClamAV anti-virus utility for Unix - command-line interface"
DESCRIPTION = "ClamAV is an open source antivirus engine for detecting trojans, viruses, malware & other malicious threats."
HOMEPAGE = "http://www.clamav.net/index.html"
SECTION = "security"
LICENSE = "LGPL-2.1"

DEPENDS = "libtool db libmspack chrpath-replacement-native"

LIC_FILES_CHKSUM = "file://COPYING.LGPL;beginline=2;endline=3;md5=4b89c05acc71195e9a06edfa2fa7d092"

SRC_URI = "http://www.clamav.net/downloads/production/${BPN}-${PV}.tar.gz \
    file://clamd.conf \
    file://freshclam.conf \
    file://volatiles.03_clamav \
    file://mempool_build_fix.patch \
    file://remove_rpath_chk.patch \
"
SRC_URI[md5sum] = "cf1f3cbe62a08c9165801f79239166ff"
SRC_URI[sha256sum] = "e144689122d3f91293808c82cbb06b7d3ac9eca7ae29564c5d148ffe7b25d58a"

LEAD_SONAME = "libclamav.so"
SO_VER = "7.1.1"

EXTRANATIVEPATH += "chrpath-native"

inherit autotools-brokensep pkgconfig useradd systemd 

UID = "clamav"
GID = "clamav"

PACKAGECONFIG ?= "ncurses openssl bz2 zlib "
PACKAGECONFIG += " ${@bb.utils.contains("DISTRO_FEATURES", "ipv6", "ipv6", "", d)}"
PACKAGECONFIG += "${@base_contains('DISTRO_FEATURES', 'systemd', 'systemd', '', d)}"
PACKAGECONFIG[pcre] = "--with-pcre=${STAGING_LIBDIR},  --without-pcre, libpcre"
PACKAGECONFIG[xml] = "--with-xml=${STAGING_LIBDIR}/.., --with-xml=no, libxml2,"
PACKAGECONFIG[json] = "--with-libjson=${STAGING_LIBDIR}, --without-libjson, json,"
PACKAGECONFIG[curl] = "--with-libcurl=${STAGING_LIBDIR}, --without-libcurl, curl,"
PACKAGECONFIG[ipv6] = "--enable-ipv6, --disable-ipv6"
PACKAGECONFIG[openssl] = "--with-openssl=${STAGING_DIR_HOST}/usr, --without-openssl, openssl, openssl"
PACKAGECONFIG[zlib] = "--with-zlib=${STAGING_DIR_HOST}/usr, --without-zlib, zlib, "
PACKAGECONFIG[bz2] = "--with-libbz2-prefix=${STAGING_LIBDIR}/.., --without-libbz2-prefix, "
PACKAGECONFIG[ncurses] = "--with-libncurses-prefix=${STAGING_LIBDIR}/.., --without-libncurses-prefix, ncurses, "

PACKAGECONFI[systemd] = "--with-systemdsystemunitdir=${systemd_unitdir}/system/', '--without-systemdsystemunitdir', "

EXTRA_OECONF += " --with-user=${UID}  --with-group=${GID} \
            --without-libcheck-prefix --disable-unrar \
            --disable-mempool \
            --program-prefix="" \
            --disable-yara \
            --disable-rpath \
            "

do_configure () {
    cd ${S}
    ./configure ${CONFIGUREOPTS} ${EXTRA_OECONF} 
}

do_compile_append() {
    # brute force removing RPATH
    chrpath -d  ${B}/libclamav/.libs/libclamav.so.${SO_VER}
    chrpath -d  ${B}/sigtool/.libs/sigtool
    chrpath -d  ${B}/clambc/.libs/clambc
    chrpath -d  ${B}/clamscan/.libs/clamscan
    chrpath -d  ${B}/clamconf/.libs/clamconf
    chrpath -d  ${B}/clamd/.libs/clamd
    chrpath -d  ${B}/freshclam/.libs/freshclam
}

do_install_append() {
    install -d ${D}/${sysconfdir}
    install -d ${D}/${localstatedir}/lib/clamav
    install -d ${D}${sysconfdir}/clamav ${D}${sysconfdir}/default/volatiles

    install -m 644 ${WORKDIR}/clamd.conf ${D}/${sysconfdir}
    install -m 644 ${WORKDIR}/freshclam.conf ${D}/${sysconfdir}
    install -m 0644 ${WORKDIR}/volatiles.03_clamav  ${D}${sysconfdir}/default/volatiles/volatiles.03_clamav
    sed -i -e 's#${STAGING_DIR_HOST}##g' ${D}${libdir}/pkgconfig/libclamav.pc
    rm ${D}/${libdir}/libclamav.so
}

pkg_postinst_${PN} () {
    if [ -z "$D" ] && [ -e /etc/init.d/populate-volatile.sh ] ; then
        ${sysconfdir}/init.d/populate-volatile.sh update
    fi
    chown ${UID}:${GID} ${localstatedir}/lib/clamav
}


PACKAGES = "${PN} ${PN}-dev ${PN}-dbg ${PN}-daemon ${PN}-doc \
            ${PN}-clamdscan ${PN}-freshclam ${PN}-libclamav ${PN}-staticdev"

FILES_${PN} = "${bindir}/clambc ${bindir}/clamscan ${bindir}/clamsubmit \
                ${bindir}/*sigtool ${mandir}/man1/clambc* ${mandir}/man1/clamscan* \
                ${mandir}/man1/sigtool* ${mandir}/man1/clambsubmit*  \
                ${docdir}/clamav/* "

FILES_${PN}-clamdscan = " ${bindir}/clamdscan \
                        ${docdir}/clamdscan/* \
                        ${mandir}/man1/clamdscan* \
                        "

FILES_${PN}-daemon = "${bindir}/clamconf ${bindir}/clamdtop ${sbindir}/clamd \
                        ${mandir}/man1/clamconf* ${mandir}/man1/clamdtop* \
                        ${mandir}/man5/clamd*  ${mandir}/man8/clamd* \
                        ${sysconfdir}/clamd.conf* \
                        ${systemd_unitdir}/system/clamav-daemon/* \
                        ${docdir}/clamav-daemon/*  ${sysconfdir}/clamav-daemon \
                        ${sysconfdir}/logcheck/ignore.d.server/clamav-daemon "

FILES_${PN}-freshclam = "${bindir}/freshclam \
                        ${sysconfdir}/freshclam.conf*  \
                        ${sysconfdir}/clamav ${sysconfdir}/default/volatiles \
                        ${localstatedir}/lib/clamav \
                        ${docdir}/${PN}-freshclam ${mandir}/man1/freshclam.* \
                        ${mandir}/man5/freshclam.conf.*"

FILES_${PN}-dev = " ${bindir}/clamav-config ${libdir}/*.la \
                    ${libdir}/pkgconfig/*.pc \
                    ${mandir}/man1/clamav-config.* \
                    ${includedir}/*.h ${docdir}/libclamav* "

FILES_${PN}-staticdev = "${libdir}/*.a"

FILES_${PN}-libclamav = "${libdir}/libclamav.so* ${libdir}/libmspack.so*\
                          ${docdir}/libclamav/* "

FILES_${PN}-doc = "${mandir}/man/* \
                   ${datadir}/man/* \
                   ${docdir}/* "

USERADD_PACKAGES = "${PN}"
GROUPADD_PARAM_${PN} = "--system ${UID}"
USERADD_PARAM_${PN} = "--system -g ${GID} --home-dir  \
    ${localstatedir}/spool/${BPN} \
    --no-create-home  --shell /bin/false ${BPN}"

RPROVIDES_${PN} += "${PN}-systemd"
RREPLACES_${PN} += "${PN}-systemd"
RCONFLICTS_${PN} += "${PN}-systemd"
SYSTEMD_SERVICE_${PN} = "${BPN}.service"

RDEPENDS_${PN} += "openssl ncurses-libncurses libbz2 ncurses-libtinfo clamav-freshclam clamav-libclamav"
