SHELLEYC = shelleyc
SHELLEYVIZ = shelleyv

all: scy pdf

pdf: simple_button.pdf led_strict.pdf ledbutton.pdf

scy: ledbutton.scy

ledbutton.scy: ledbutton.yml simple_button.scy led_strict.scy
	# This is ok: led is more strict but ledbutton is also more strict
	$(SHELLEYC) -d $< -u simple_button.scy\:SimpleButton led_strict.scy\:LedStrict

%.scy: %.yml
	$(SHELLEYC) -d $<

%.gv: %.scy
	$(SHELLEYVIZ) $< -o $@

%.pdf: %.gv
	dot -Tpdf -o $@ $<

clean:
	rm -f *.scy *.pdf *.gv

.SUFFIXES: .yml .scy
