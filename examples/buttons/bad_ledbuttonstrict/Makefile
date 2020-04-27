PYTHON = PYTHONPATH=../../../ python3
SHELLYC = $(PYTHON) -m shelleyc
SHELLYVIZ = $(PYTHON) -m shelleyv

all: scy pdf

pdf: simple_button.pdf led_strict.pdf

scy: ledbutton.scy

ledbutton.scy: ledbutton.yml simple_button.scy led_strict.scy
	# Invalid device: TriggerIntegrationFailure(error_trace=('b2.pressed', 'led2.on', 'b2.pressed', 'led2.on'), component_errors={'led2': (['on', 'on'], 1)})
	! $(SHELLYC) -d $< -u simple_button.scy\:SimpleButton led_strict.scy\:LedStrict

%.scy: %.yml
	$(SHELLYC) -d $<

%.gv: %.scy
	$(SHELLYVIZ) $< -o $@

%.pdf: %.gv
	dot -Tpdf -o $@ $<

clean:
	rm -f *.scy *.pdf *.gv

.SUFFIXES: .yml .scy
