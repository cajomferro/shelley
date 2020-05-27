SHELLEYC = shelleyc
SHELLEYV = shelleyv

all: scy

pdf: button.pdf timer.pdf clickbutton.pdf

scy: clickbutton.scy

clickbutton.scy: clickbutton.yml timer.scy button.scy
	$(SHELLEYC) -d $< -uf uses.yml -o $@

%.scy: %.yml
	$(SHELLEYC) -d $< -o $@

clickbutton-micro-dfa-minimized.scy clickbutton-micro-dfa-minimized-no-traps.scy clickbutton-micro-nfa-with-epsilon-no-traps.scy: clickbutton.yml
	$(SHELLEYC) -d clickbutton.yml -uf uses.yml --no-output --skip-testing -i

internal: clickbutton-micro-dfa-minimized-no-traps.png clickbutton-micro-nfa-with-epsilon-no-traps.png

desklamp-%.scy:
	test -f $<

%.gv: %.scy
	$(SHELLEYV) $< -o $@

%.pdf: %.gv
	dot -Tpdf -o $@ $<

%.png: %.gv
	dot -Tpng -o $@ $<

clean:
	rm -f *.scy *.pdf *.gv

.PHONY: all pdf scy

.SUFFIXES: .yml .scy
