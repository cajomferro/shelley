include ../common.mk

MAKEFLAGS += --no-print-directory

USES = -u uses.yml
#VALIDITY_CHECKS=--skip-direct
#VALIDITY_CHECKS=--skip-mc
SHELLEYPY_OPTS = # --optimize --include-iface-ops

all: scy

pdf: smartbutton.pdf

png: smartbutton.png

scy: deps
	$(MAKE) smartbutton.scy

USES = -u uses.yml



deps:
	$(MAKE) -C ../base pressed_button.scy

smartbutton-stats.json:
	$(MAKE) -C ../base pressed_button-stats.json
	$(MAKE) smartbutton-stats.json

stats: smartbutton-stats.json

clean:
	rm -f *.scy *.pdf *.png *.gv *-stats.json *.int *.smv
	$(MAKE) -C ../base clean


.PHONY: all pdf scy deps clean

