SHELLEYC = shelleyc
SHELLEYV = shelleyv

all: scy

pdf: simple_button.pdf led_strict.pdf desklamp.pdf

scy: desklamp.scy

desklamp.scy: desklamp.yml led_strict.scy simple_button.scy
	$(SHELLEYC) -d $< -u simple_button.scy\:SimpleButton led_strict.scy\:LedStrict

%.scy: %.yml
	$(SHELLEYC) -d $< -o $@
	test -f $<

# run with make internal SHELLEYC="shelleyc -i"
internal: pdf desklamp-micro-dfa-minimized.pdf desklamp-micro-dfa-minimized-no-traps.pdf desklamp-micro-nfa-no-epsilon-no-traps.pdf desklamp-shuffle-dfa-minimized.pdf desklamp-shuffle-dfa-minimized-no-traps.pdf

desklamp-%.scy:
	test -f $<

%.gv: %.scy
	$(SHELLEYV) -o $@ $<

%.pdf: %.gv
	dot -Tpdf -o $@ $<

desklamp-%.scy:
	test -f $<

clean:
	rm -f *.scy *.pdf *.gv

.PHONY: scy clean all pdf

.SUFFIXES: .yml .scy
