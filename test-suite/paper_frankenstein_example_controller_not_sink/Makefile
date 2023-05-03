include ../common.mk

MAKEFLAGS += --no-print-directory

USES = -u uses.yml
#VALIDITY_CHECKS=--skip-direct
#VALIDITY_CHECKS=--skip-mc
SHELLEYPY_OPTS = # --optimize --include-iface-ops

all: scy

pdf: controller.pdf

png: controller.png

scy: deps
	$(MAKE) controller.scy

USES = -u uses.yml



deps:
	$(MAKE) -C ../paper_frankenstein_example valve.scy
	$(MAKE) -C ../paper_frankenstein_example timer.scy

paper_frankenstein_example_controller_not_sink-stats.json:
	$(MAKE) -C ../paper_frankenstein_example valve-stats.json
	$(MAKE) -C ../paper_frankenstein_example timer-stats.json
	$(MAKE) controller-stats.json

stats: paper_frankenstein_example_controller_not_sink-stats.json

clean:
	rm -f *.scy *.pdf *.png *.gv *-stats.json *.int *.smv
	$(MAKE) -C ../paper_frankenstein_example clean
	$(MAKE) -C ../paper_frankenstein_example clean


.PHONY: all pdf scy deps clean

