include ../common.mk
USES = -u uses.yml

all: scy

scy: controller.scy

USES = -u uses.yml

deps_scy:
	$(MAKE) -C ../paper_frankenstein_example valve.scy
	$(MAKE) -C ../paper_frankenstein_example timer.scy


controller.scy: controller.shy deps_scy
	! $(SHELLEYMC) $(USES) -s $< $(VALIDITY_CHECKS) $(DEBUG)

clean:
	rm -f *.scy *.pdf *.png *.gv *-stats.json *.int *.smv
	$(MAKE) -C ../paper_frankenstein_example clean
	$(MAKE) -C ../paper_frankenstein_example clean


.PHONY: all pdf scy deps clean

