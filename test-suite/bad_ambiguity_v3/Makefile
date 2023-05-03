# AmbiguityFailure(micro_trace=('b.pressed', 't.start', 'b.released', 't.cancel', 't.start', 't.timeout'), macro_traces=(('buttonPressedTwice',), ('buttonPressedOnce',)))

include ../common.mk
USES = -u uses.yml

# WARNING: NuSMV doesn't check ambiguity!


all: scy

scy: ambiguous.scy

USES = -u uses.yml

deps_scy:
	$(MAKE) singleclick.scy
	$(MAKE) -C ../base timer.scy

ambiguous.scy: ambiguous.shy deps_scy
	! $(SHELLEYC) $(USES) -d $< --check-ambiguity $(DEBUG)

clean:
	rm -f *.scy *.pdf *.png *.gv *-stats.json *.int *.smv
	$(MAKE) -C ../base clean


.PHONY: all pdf scy deps clean smv

