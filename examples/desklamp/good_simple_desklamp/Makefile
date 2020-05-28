SHELLEYC = shelleyc
SHELLEYV = shelleyv

all: scy

pdf: simple_button.pdf led_strict.pdf desklamp.pdf

scy: desklamp.scy

desklamp.scy: desklamp.yml led_strict.scy simple_button.scy

%.scy: %.yml
	$(SHELLEYC) -u uses.yml -d $< -o $@

%.gv: %.scy
	$(SHELLEYV) $< -o $@

%.pdf: %.gv
	dot -Tpdf -o $@ $<

clean:
	rm -f *.scy *.pdf *.gv


.SUFFIXES: .yml .scy
