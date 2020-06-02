SHELLEYC = shelleyc
SHELLEYV = shelleyv

all: scy

pdf: simple_button.pdf led_strict.pdf ledbutton.pdf

scy: ledbutton.scy

# This is ok: led is more strict but ledbutton is also more strict
ledbutton.scy: ledbutton.yml simple_button.scy led_strict.scy

%.scy: %.yml
	$(SHELLEYC) -u uses.yml -d $<

%.gv: %.scy
	$(SHELLEYV) $< -o $@

%.pdf: %.gv
	dot -Tpdf -o $@ $<

clean:
	rm -f *.scy *.pdf *.gv

.SUFFIXES: .yml .scy
