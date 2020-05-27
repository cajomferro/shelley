SHELLEYC = shelleyc
SHELLEYV = shelleyv

all: scy

pdf: button.pdf led.pdf timer.pdf desklamp.pdf

scy: desklamp.scy

desklamp.scy: desklamp.yml timer.scy led.scy button.scy
	$(SHELLEYC) -d $< -uf uses.yml -o $@ # -v
	test -f $<

%.scy: %.yml
	$(SHELLEYC) -d $< -o $@
	test -f $<

# run with make internal SHELLEYC="shelleyc -i"
internal: pdf desklamp-micro-dfa-minimized.pdf desklamp-micro-dfa-minimized-no-traps.pdf desklamp-micro-nfa-no-epsilon-no-traps.pdf desklamp-micro-nfa-with-epsilon-no-traps.pdf# -shuffle-dfa-minimized.pdf desklamp-shuffle-dfa-minimized-no-traps.pdf

desklamp-%.scy:
	test -f $<

%.gv: %.scy
	$(SHELLEYV) $< -o $@

%.pdf: %.gv
	dot -Tpdf -o $@ $<

clean:
	rm -f *.scy *.pdf *.gv

.PHONY: all pdf scy

.SUFFIXES: .yml .scy
