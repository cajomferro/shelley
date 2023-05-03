include ../common.mk

MAKEFLAGS += --no-print-directory

USES = -u uses.yml
#VALIDITY_CHECKS=--skip-direct
#VALIDITY_CHECKS=--skip-mc
SHELLEYPY_OPTS = # --optimize --include-iface-ops

all: scy

pdf: 2controllers-hard.pdf

png: 2controllers-hard.png

scy: deps
	$(MAKE) 2controllers-hard.scy

USES = -u uses.yml



deps:
	$(MAKE) valve.scy
	$(MAKE) timer.scy
	$(MAKE) controller.scy

2controllers_v2_hard-stats.json:
	$(MAKE) valve-stats.json
	$(MAKE) timer-stats.json
	$(MAKE) controller-stats.json
	$(MAKE) 2controllers-hard-stats.json

stats: 2controllers_v2_hard-stats.json

clean:
	rm -f *.scy *.pdf *.png *.gv *-stats.json *.int *.smv


.PHONY: all pdf scy deps clean

