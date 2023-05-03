include ../common.mk

MAKEFLAGS += --no-print-directory

USES = -u uses.yml
#VALIDITY_CHECKS=--skip-direct
#VALIDITY_CHECKS=--skip-mc
SHELLEYPY_OPTS = # --optimize --include-iface-ops

all: scy

pdf: aquamote.pdf

png: aquamote.png

scy: deps
	$(MAKE) aquamote.scy

USES = -u uses.yml



deps:

aquamote_cpp_var3-stats.json:
	$(MAKE) aquamote-stats.json

stats: aquamote_cpp_var3-stats.json

clean:
	rm -f *.scy *.pdf *.png *.gv *-stats.json *.int *.smv


.PHONY: all pdf scy deps clean

