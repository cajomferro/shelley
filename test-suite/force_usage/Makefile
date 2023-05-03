include ../common.mk

MAKEFLAGS += --no-print-directory

USES = -u uses.yml
#VALIDITY_CHECKS=--skip-direct
#VALIDITY_CHECKS=--skip-mc
SHELLEYPY_OPTS = # --optimize --include-iface-ops

all: scy

pdf: app.pdf

png: app.png

scy: deps
	$(MAKE) app.scy

USES = -u uses.yml



deps:
	$(MAKE) led.scy

force_usage-stats.json:
	$(MAKE) led-stats.json
	$(MAKE) app-stats.json

stats: force_usage-stats.json

clean:
	rm -f *.scy *.pdf *.png *.gv *-stats.json *.int *.smv


.PHONY: all pdf scy deps clean

