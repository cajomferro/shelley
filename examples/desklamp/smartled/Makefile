SHELLEYC = shelleyc
SHELLEYV = shelleyv

all: scy

pdf: led.pdf timer.pdf smartled.pdf

scy: smartled.scy

smartled.scy: smartled.yml timer.scy led.scy

%.scy: %.yml
	$(SHELLEYC) -u uses.yml -d $< -o $@

# run with make internal SHELLEYC="shelleyc -i"
internal: pdf smartled-micro-dfa-minimized.pdf smartled-micro-dfa-minimized-no-traps.pdf smartled-micro-nfa-no-epsilon-no-traps.pdf smartled-micro-nfa-with-epsilon-no-traps.pdf# -shuffle-dfa-minimized.pdf smartled-shuffle-dfa-minimized-no-traps.pdf

%.gv: %.scy
	$(SHELLEYV) $< -o $@

%.pdf: %.gv
	dot -Tpdf -o $@ $<

clean:
	rm -f *.scy *.pdf *.gv

.PHONY: all pdf scy

.SUFFIXES: .yml .scy
