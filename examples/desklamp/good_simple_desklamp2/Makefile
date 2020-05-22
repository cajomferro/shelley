SHELLEYC = shelleyc
SHELLEYV = shelleyv

all: scy pdf

pdf: simple_button.pdf led_strict.pdf desklamp.pdf desklamp-micro-dfa-minimized.pdf desklamp-micro-dfa-minimized-no-traps.pdf desklamp-micro-nfa-no-epsilon-no-traps.pdf desklamp-shuffle-dfa-minimized.pdf desklamp-shuffle-dfa-minimized-no-traps.pdf

scy: desklamp.scy

desklamp.scy: desklamp.yml led_strict.scy simple_button.scy
	$(SHELLEYC) -i -d $< -u simple_button.scy\:SimpleButton led_strict.scy\:LedStrict -v

%.scy: %.yml
	$(SHELLEYC) -d $< -o $@
	test -f $<

%.gv: %.scy
	$(SHELLEYV) $< -o $@

%.pdf: %.gv
	dot -Tpdf -o $@ $<

desklamp-%.scy:
	test -f $<

clean:
	rm -f *.scy *.pdf *.gv

.SUFFIXES: .yml .scy
