include ../common.mk

MAKEFLAGS += --no-print-directory

USES = -u uses.yml
#VALIDITY_CHECKS=--skip-direct
#VALIDITY_CHECKS=--skip-mc
SHELLEYPY_OPTS = # --optimize --include-iface-ops

all: scy

pdf: clickbutton.pdf

png: clickbutton.png

scy: deps
	$(MAKE) clickbutton.scy

USES = -u uses.yml



deps:
	$(MAKE) -C ../base timer.scy
	$(MAKE) -C ../base button.scy

clickbutton-stats.json:
	$(MAKE) -C ../base timer-stats.json
	$(MAKE) -C ../base button-stats.json
	$(MAKE) clickbutton-stats.json

stats: clickbutton-stats.json

clean:
	rm -f *.scy *.pdf *.png *.gv *-stats.json *.int *.smv
	$(MAKE) -C ../base clean
	$(MAKE) -C ../base clean


.PHONY: all pdf scy deps clean

