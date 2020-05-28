SHELLEYC = shelleyc
SHELLEYV = shelleyv

all: scy

pdf: button.pdf timer.pdf clickbutton.pdf

scy: clickbutton.scy

clickbutton.scy: clickbutton.yml timer.scy button.scy

%.scy: %.yml
	$(SHELLEYC) -u uses.yml -d $< -o $@

# run with make internal SHELLEYC="shelleyc -i"
internal: pdf clickbutton-micro-dfa-minimized.pdf clickbutton-micro-dfa-minimized-no-traps.pdf clickbutton-micro-nfa-no-epsilon-no-traps.pdf clickbutton-micro-nfa-with-epsilon-no-traps.pdf# -shuffle-dfa-minimized.pdf clickbutton-shuffle-dfa-minimized-no-traps.pdf

#clickbutton-%.scy:
#	test -f $<

%.gv: %.scy
	$(SHELLEYV) $< -o $@

%.pdf: %.gv
	dot -Tpdf -o $@ $<

clean:
	rm -f *.scy *.pdf *.gv

.PHONY: all pdf scy

.SUFFIXES: .yml .scy
