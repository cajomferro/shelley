SHELLEYC = shelleyc
SHELLEYV = shelleyv

all: scy

pdf: button.pdf timer.pdf smartbutton.pdf

# run with make internal SHELLEYC="shelleyc -i"
internal: pdf smartbutton-micro-dfa-minimized.pdf smartbutton-micro-dfa-minimized-no-traps.pdf smartbutton-micro-nfa-no-epsilon-no-traps.pdf smartbutton-micro-nfa-with-epsilon-no-traps.pdf

scy: smartbutton.scy

smartbutton.scy: smartbutton.yml button.scy timer.scy

%.scy: %.yml
	$(SHELLEYC) -u uses.yml -d $<

%.gv: %.scy
	$(SHELLEYV) $< -o $@

%.pdf: %.gv
	dot -Tpdf -o $@ $<

clean:
	rm -f *.scy *.pdf *.gv