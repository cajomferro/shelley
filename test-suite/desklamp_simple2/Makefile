include ../common.mk

MAKEFLAGS += --no-print-directory

USES = -u uses.yml
#VALIDITY_CHECKS=--skip-direct
#VALIDITY_CHECKS=--skip-mc
SHELLEYPY_OPTS = # --optimize --include-iface-ops

all: scy

pdf: desklamp.pdf

png: desklamp.png

scy: deps
	$(MAKE) desklamp.scy

USES = -u uses.yml



deps:
	$(MAKE) -C ../base simple_button.scy
	$(MAKE) -C ../base led_strict.scy

desklamp_simple2-stats.json:
	$(MAKE) -C ../base simple_button-stats.json
	$(MAKE) -C ../base led_strict-stats.json
	$(MAKE) desklamp-stats.json

stats: desklamp_simple2-stats.json

clean:
	rm -f *.scy *.pdf *.png *.gv *-stats.json *.int *.smv
	$(MAKE) -C ../base clean
	$(MAKE) -C ../base clean


.PHONY: all pdf scy deps clean

