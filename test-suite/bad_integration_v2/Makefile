include ../common.mk
USES = -u uses.yml

all: scy

scy: clickbutton.scy

USES = -u uses.yml

deps_scy:
	$(MAKE) -C ../base timer.scy
	$(MAKE) -C ../base button.scy


clickbutton.scy: clickbutton.shy deps_scy
	! $(SHELLEYMC) $(USES) -s $< $(VALIDITY_CHECKS) $(DEBUG)

clean:
	rm -f *.scy *.pdf *.png *.gv *-stats.json *.int *.smv
	$(MAKE) -C ../base clean
	$(MAKE) -C ../base clean


.PHONY: all pdf scy deps clean

