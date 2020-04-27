SHELLEYC = shelleyc
SHELLEYVIZ = shelleyv

all: scy pdf

pdf: simple_button.pdf led_strict.pdf desklamp.pdf desklamp-shuffle-dfa desklamp-internal-nfa desklamp-internal-dfa

scy: desklamp.scy

desklamp.scy: desklamp.yml led_strict.scy simple_button.scy
	$(SHELLEYC) -i -d $< -u simple_button.scy\:SimpleButton led_strict.scy\:LedStrict

%.scy: %.yml
	$(SHELLEYC) -d $< -o $@
	test -f $<

%.gv: %.scy
	$(SHELLEYVIZ) $< -o $@

%.pdf: %.gv
	dot -Tpdf -o $@ $<

desklamp-shuffle-dfa:
	$(SHELLEYVIZ) -o desklamp-shuffle-dfa.gv desklamp-shuffle-dfa.scy
	dot -Tpdf -o desklamp-shuffle-dfa.pdf desklamp-shuffle-dfa.gv

desklamp-internal-nfa:
	$(SHELLEYVIZ) -o desklamp-internal-nfa.gv desklamp-internal-nfa.scy
	dot -Tpdf -o desklamp-internal-nfa.pdf desklamp-internal-nfa.gv

desklamp-internal-dfa:
	$(SHELLEYVIZ) -o desklamp-internal-dfa.gv desklamp-internal-dfa.scy
	dot -Tpdf -o desklamp-internal-dfa.pdf desklamp-internal-dfa.gv

clean:
	rm -f *.scy *.pdf *.gv

.SUFFIXES: .yml .scy
