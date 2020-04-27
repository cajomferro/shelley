SHELLEYC = shelleyc
SHELLEYVIZ = shelleyv

all: scy pdf

pdf: simple_button.pdf led_strict.pdf desklamp.pdf

scy: desklamp.scy

desklamp.scy: desklamp.yml led_strict.scy simple_button.scy
	$(SHELLEYC) -d $< -u simple_button.scy\:SimpleButton led_strict.scy\:LedStrict

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
