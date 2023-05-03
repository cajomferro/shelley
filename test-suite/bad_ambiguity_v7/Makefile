# Invalid device: AmbiguityFailure(micro_trace=('b.press', 'b.release', 'ledA.on', 't.start', 't.timeout', 'ledA.off', 'ledB.off'), macro_traces=(('level1', 'standby1'), ('level1', 'standby2')))

include ../common.mk
USES = -u uses.yml

# WARNING: NuSMV doesn't check ambiguity!

all: scy
scy: desklamp.scy

USES = -u uses.yml

deps_scy:
	$(MAKE) -C ../base timer.scy
	$(MAKE) -C ../base led_free.scy
	$(MAKE) -C ../base button.scy

desklamp.scy: desklamp.shy deps_scy
	! $(SHELLEYC) $(USES) -d $< --check-ambiguity $(DEBUG)

clean:
	rm -f *.scy *.pdf *.png *.gv *-stats.json *.int *.smv
	$(MAKE) -C ../base clean
	$(MAKE) -C ../base clean
	$(MAKE) -C ../base clean


.PHONY: all pdf scy deps clean smv

