# Invalid device: AmbiguityFailure(micro_trace=('B.press', 'T.start', 'B.release', 'T.timeout'), macro_traces=(('double',), ('single',)))

include ../common.mk
USES = -u uses.yml

# WARNING: NuSMV doesn't check ambiguity!

all: scy

scy: clickbutton.scy

USES = -u uses.yml

deps_scy:
	$(MAKE) -C ../base button.scy
	$(MAKE) -C ../base timer.scy

clickbutton.scy: clickbutton.shy deps_scy
	! $(SHELLEYC) $(USES) -d $< --check-ambiguity $(DEBUG)

clean:
	rm -f *.scy *.pdf *.png *.gv *-stats.json *.int *.smv
	$(MAKE) -C ../base clean
	$(MAKE) -C ../base clean


.PHONY: all pdf scy deps clean smv

