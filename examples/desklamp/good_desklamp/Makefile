SHELLEYC = shelleyc
SHELLEYV = shelleyv

all: scy pdf

pdf: button.pdf led.pdf timer.pdf desklamp.pdf desklamp-internal-dfa.pdf desklamp-internal-nfa.pdf desklamp-shuffle-dfa.pdf

scy: desklamp.scy

desklamp.scy: desklamp.yml timer.scy led.scy button.scy
	time $(SHELLEYC) -d $< -u button.scy\:Button led.scy\:Led timer.scy\:Timer -o $@ -i
	test -f $<

%.scy: %.yml
	time $(SHELLEYC) -d $< -o $@
	test -f $<

%.gv: %.scy
	$(SHELLEYV) $< -o $@

%.pdf: %.gv
	dot -Tpdf -o $@ $<

clean:
	rm -f *.scy *.pdf *.gv


.SUFFIXES: .yml .scy
