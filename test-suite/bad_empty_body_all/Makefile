include ../common.mk
USES = -u uses.yml

all: smv

smv: button_handler.smv

scy: button_handler.scy

USES = -u uses.yml

deps_smv:
	$(MAKE) -C ../base button.smv

deps_scy:
	$(MAKE) -C ../base button.scy

button_handler.smv: button_handler.shy deps_smv
	$(SHELLEYMC) $(USES) -s $< --skip-direct $(DEBUG)

button_handler.scy: button_handler.shy deps_scy
	! $(SHELLEYMC) $(USES) -s $< --skip-mc $(DEBUG)

clean:
	rm -f *.scy *.pdf *.png *.gv *-stats.json *.int *.smv
	$(MAKE) -C ../base clean


.PHONY: all pdf scy deps clean smv

