# Invalid device: AmbiguityFailure(micro_trace=('b2.press', 'b1.press'), macro_traces=(('button3OrOthers',), ('button1AndOther',)))

include ../common.mk
USES = -u uses.yml

# WARNING: NuSMV doesn't check ambiguity!

all: scy

scy: ambiguous.scy

USES = -u uses.yml

deps_scy:
	$(MAKE) -C ../base simple_button.scy

ambiguous.scy: ambiguous.shy deps_scy
	! $(SHELLEYC) $(USES) -d $< --check-ambiguity $(DEBUG)

clean:
	rm -f *.scy *.pdf *.png *.gv *-stats.json *.int *.smv
	$(MAKE) -C ../base clean


.PHONY: all pdf scy deps clean smv

