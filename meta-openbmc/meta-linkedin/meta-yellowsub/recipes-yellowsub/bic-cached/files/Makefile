# Copyright 2015-present Facebook. All Rights Reserved.
all: bic-cached

CFLAGS += -Wall -Werror

bic-cached: bic-cached.c
	$(CC) -pthread -lbic -std=c99 -o $@ $^ $(LDFLAGS)

.PHONY: clean

clean:
	rm -rf *.o bic-cached
