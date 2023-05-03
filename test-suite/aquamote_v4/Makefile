include ../common.mk

MAKEFLAGS += --no-print-directory

USES = -u uses.yml
#VALIDITY_CHECKS=--skip-direct
#VALIDITY_CHECKS=--skip-mc
SHELLEYPY_OPTS = # --optimize --include-iface-ops

all: scy

pdf: aquamote_controller_finalstates.pdf

png: aquamote_controller_finalstates.png

scy: deps
	$(MAKE) aquamote_controller_finalstates.scy

USES = -u uses.yml



deps:
	$(MAKE) -C ../aquamote_v1 magnetic.scy
	$(MAKE) -C ../aquamote_v1 valve.scy
	$(MAKE) lowpower-strict-finalstates.scy
	$(MAKE) radio_finalstates.scy

aquamote_v4-stats.json:
	$(MAKE) -C ../aquamote_v1 magnetic-stats.json
	$(MAKE) -C ../aquamote_v1 valve-stats.json
	$(MAKE) lowpower-strict-finalstates-stats.json
	$(MAKE) radio_finalstates-stats.json
	$(MAKE) aquamote_controller_finalstates-stats.json

stats: aquamote_v4-stats.json

clean:
	rm -f *.scy *.pdf *.png *.gv *-stats.json *.int *.smv
	$(MAKE) -C ../aquamote_v1 clean
	$(MAKE) -C ../aquamote_v1 clean


.PHONY: all pdf scy deps clean

