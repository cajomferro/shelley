include ../common.mk

MAKEFLAGS += --no-print-directory

USES = -u uses.yml
#VALIDITY_CHECKS=--skip-direct
#VALIDITY_CHECKS=--skip-mc
SHELLEYPY_OPTS = # --optimize --include-iface-ops

all: scy

pdf: button_handler.pdf

png: button_handler.png

scy: deps
	$(MAKE) button_handler.scy

USES = -u uses.yml



deps:
	$(MAKE) -C ../base button.scy

empty_body-stats.json:
	$(MAKE) -C ../base button-stats.json
	$(MAKE) button_handler-stats.json

stats: empty_body-stats.json

clean:
	rm -f *.scy *.pdf *.png *.gv *-stats.json *.int *.smv
	$(MAKE) -C ../base clean


.PHONY: all pdf scy deps clean

