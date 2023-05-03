include ../common.mk
USES = -u uses.yml

all: scy

scy: aquamote_core.scy

USES = -u uses.yml

deps_scy:
	$(MAKE) -C ../paper_aquamote magnetic.scy
	$(MAKE) -C ../paper_aquamote power_handler.scy
	$(MAKE) -C ../paper_aquamote valve.scy
	$(MAKE) -C ../paper_aquamote timer.scy
	$(MAKE) -C ../paper_aquamote valvehandler.scy
	$(MAKE) -C ../paper_aquamote httpclient.scy
	$(MAKE) -C ../paper_aquamote gprsclient.scy
	$(MAKE) -C ../paper_aquamote wireless.scy


aquamote_core.scy: aquamote_core.shy deps_scy
	! $(SHELLEYMC) $(USES) -s $< $(VALIDITY_CHECKS) $(DEBUG)

clean:
	rm -f *.scy *.pdf *.png *.gv *-stats.json *.int *.smv
	$(MAKE) -C ../paper_aquamote clean
	$(MAKE) -C ../paper_aquamote clean
	$(MAKE) -C ../paper_aquamote clean
	$(MAKE) -C ../paper_aquamote clean
	$(MAKE) -C ../paper_aquamote clean
	$(MAKE) -C ../paper_aquamote clean
	$(MAKE) -C ../paper_aquamote clean
	$(MAKE) -C ../paper_aquamote clean


.PHONY: all pdf scy deps clean

