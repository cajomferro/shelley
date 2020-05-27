SHELLEYC = shelleyc
SHELLEYV = shelleyv

all: scy

pdf: button.pdf timer.pdf smartbutton.pdf

scy: smartbutton.scy

smartbutton.scy: smartbutton.yml button.scy timer.scy
	$(SHELLEYC) -d $< -u button.scy\:Button timer.scy\:Timer

# run with make internal SHELLEYC="shelleyc -i"
internal: pdf smartbutton-micro-dfa-minimized.pdf smartbutton-micro-dfa-minimized-no-traps.pdf smartbutton-micro-nfa-no-epsilon-no-traps.pdf smartbutton-micro-nfa-with-epsilon-no-traps.pdf

%.scy: %.yml
	$(SHELLEYC) -d $<

%.gv: %.scy
	$(SHELLEYV) $< -o $@

%.pdf: %.gv
	dot -Tpdf -o $@ $<

clean:
	rm -f *.scy *.pdf *.gv