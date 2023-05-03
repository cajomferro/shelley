include ../common.mk
USES = -u uses.yml

all: scy

scy: controller.scy

USES = -u uses.yml

deps_scy:
	$(MAKE) bit.scy


controller.scy: controller.shy deps_scy
	! $(SHELLEYMC) $(USES) -s $< $(VALIDITY_CHECKS) $(DEBUG)

clean:
	rm -f *.scy *.pdf *.png *.gv *-stats.json *.int *.smv


.PHONY: all pdf scy deps clean

