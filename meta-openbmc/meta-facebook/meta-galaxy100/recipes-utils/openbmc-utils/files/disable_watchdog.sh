#!/bin/sh

. /usr/local/bin/openbmc-utils.sh

# Disable the dual boot watch dog
devmem_clear_bit 0x1e78502c 0

# Disable the watch dog
devmem_clear_bit 0x1e78500c 0
