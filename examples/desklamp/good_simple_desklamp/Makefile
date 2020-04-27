PYTHON = PYTHONPATH=../../../ python3
SHELLYC = $(PYTHON) -m shelleyc
SHELLYVIZ = $(PYTHON) -m shelleyv

all: scy pdf

pdf: simple_button.pdf led_strict.pdf desklamp.pdf

scy: desklamp.scy

desklamp.scy: desklamp.yml led_strict.scy simple_button.scy
	$(SHELLYC) -d $< -u simple_button.scy\:SimpleButton led_strict.scy\:LedStrict

%.scy: %.yml
	$(SHELLYC) -d $< -o $@
	test -f $<

%.gv: %.scy
	$(SHELLYVIZ) $< -o $@

%.pdf: %.gv
	dot -Tpdf -o $@ $<

clean:
	rm -f *.scy *.pdf *.gv


.SUFFIXES: .yml .scy
