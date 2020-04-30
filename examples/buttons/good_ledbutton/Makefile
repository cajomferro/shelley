SHELLEYC = shelleyc
SHELLEYV = shelleyv

all: scy pdf

pdf: simple_button.pdf led.pdf ledbutton.pdf

scy: ledbutton.scy

ledbutton.scy: ledbutton.yml simple_button.scy led.scy
	# This is ok: led is more strict but ledbutton is also more strict
	$(SHELLEYC) -d $< -u simple_button.scy\:SimpleButton led.scy\:Led

%.scy: %.yml
	$(SHELLEYC) -d $<

%.gv: %.scy
	$(SHELLEYV) $< -o $@

%.pdf: %.gv
	dot -Tpdf -o $@ $<

clean:
	rm -f *.scy *.pdf *.gv

.SUFFIXES: .yml .scy
