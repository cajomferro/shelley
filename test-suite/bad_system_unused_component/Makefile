include ../common.mk
USES = -u uses.yml

all: smv

smv: desklamp.smv

scy: desklamp.scy

USES = -u uses.yml

deps_smv:
	$(MAKE) -C ../base led.smv
	$(MAKE) -C ../base button.smv

deps_scy:
	$(MAKE) -C ../base led.scy
	$(MAKE) -C ../base button.scy

desklamp.smv: desklamp.shy deps_smv
	# WARNING: NuSMV doesn't check this! https://gitlab.com/safeiot/shelley-checker/-/issues/55
	$(SHELLEYMC) $(USES) -s $< --skip-direct $(DEBUG)

desklamp.scy: desklamp.shy deps_scy
	! $(SHELLEYMC) $(USES) -s $< --skip-mc $(DEBUG)

clean:
	rm -f *.scy *.pdf *.png *.gv *-stats.json *.int *.smv
	$(MAKE) -C ../base clean
	$(MAKE) -C ../base clean


.PHONY: all pdf scy deps clean smv

