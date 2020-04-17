PYTHON = PYTHONPATH=../../../ python3
SHELLYC = $(PYTHON) -m appcompiler
SHELLYVIZ = $(PYTHON) -m appvizviewer

all: scy pdf

pdf: simple_button.pdf led_strict.pdf desklamp.pdf desklamp-internal-nfa desklamp-internal-dfa

scy: desklamp.scy

desklamp.scy: desklamp.yml led_strict.scy simple_button.scy
	$(SHELLYC) -i -d $< -u simple_button.scy\:SimpleButton led_strict.scy\:LedStrict

%.scy: %.yml
	$(SHELLYC) -d $< -o $@
	test -f $<

%.gv: %.scy
	$(SHELLYVIZ) $< -o $@

%.pdf: %.gv
	dot -Tpdf -o $@ $<

desklamp-internal-nfa:
	$(SHELLYVIZ) -o desklamp-internal-nfa.gv desklamp-internal-nfa.scy
	dot -Tpdf -o desklamp-internal-nfa.pdf desklamp-internal-nfa.gv

desklamp-internal-dfa:
	$(SHELLYVIZ) -o desklamp-internal-dfa.gv desklamp-internal-dfa.scy
	dot -Tpdf -o desklamp-internal-dfa.pdf desklamp-internal-dfa.gv

clean:
	rm -f *.scy *.pdf *.gv

.SUFFIXES: .yml .scy
