SHELLEYC = shelleyc
SHELLEYV = shelleyv

all: scy

pdf: button.pdf led.pdf sendok.pdf

scy: sendok.scy

sendok.scy: sendok.yml led.scy button.scy
	$(SHELLEYC) -d $< -u button.scy\:Button led.scy\:Led

%.scy: %.yml
	$(SHELLEYC) -d $< -o $@
	test -f $<

%.gv: %.scy
	$(SHELLEYV) $< -o $@

%.pdf: %.gv
	dot -Tpdf -o $@ $<

clean:
	rm -f *.scy *.pdf *.gv


.SUFFIXES: .yml .scy