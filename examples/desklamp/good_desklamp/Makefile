SHELLEYC = shelleyc
SHELLEYVIZ = shelleyv

all: scy pdf

pdf: button.pdf led.pdf timer.pdf desklamp.pdf

scy: desklamp.scy

desklamp.scy: desklamp.yml timer.scy led.scy button.scy
	$(SHELLEYC) -d $< -u button.scy\:Button led.scy\:Led timer.scy\:Timer

%.scy: %.yml
	$(SHELLEYC) -d $< -o $@
	test -f $<

%.gv: %.scy
	$(SHELLEYVIZ) $< -o $@

%.pdf: %.gv
	dot -Tpdf -o $@ $<

clean:
	rm -f *.scy *.pdf *.gv


.SUFFIXES: .yml .scy
