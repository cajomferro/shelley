include ../common.mk

MAKEFLAGS += --no-print-directory

USES = -u uses.yml
#VALIDITY_CHECKS=--skip-direct
#VALIDITY_CHECKS=--skip-mc
SHELLEYPY_OPTS = # --optimize --include-iface-ops

all: scy

pdf: valvehandler.pdf

png: valvehandler.png

scy: deps
	$(MAKE) valvehandler.scy

USES = -u uses.yml



deps:
	$(MAKE) valve.scy
	$(MAKE) timer.scy

valvehandlerNOloop_op1-stats.json:
	$(MAKE) valve-stats.json
	$(MAKE) timer-stats.json
	$(MAKE) valvehandler-stats.json

stats: valvehandlerNOloop_op1-stats.json

clean:
	rm -f *.scy *.pdf *.png *.gv *-stats.json *.int *.smv


.PHONY: all pdf scy deps clean

