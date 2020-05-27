SHELLEYC = shelleyc
SHELLEYV = shelleyv

all: scy

pdf: simple_button.pdf led_strict.pdf

scy: ledbutton.scy

ledbutton.scy: ledbutton.yml simple_button.scy led_strict.scy
	# Invalid device: TriggerIntegrationFailure(error_trace=('b2.pressed', 'led2.on', 'b2.pressed', 'led2.on'), component_errors={'led2': (['on', 'on'], 1)})
	! $(SHELLEYC) -d $< -u simple_button.scy\:SimpleButton led_strict.scy\:LedStrict

%.scy: %.yml
	$(SHELLEYC) -d $<

%.gv: %.scy
	$(SHELLEYV) $< -o $@

%.pdf: %.gv
	dot -Tpdf -o $@ $<

clean:
	rm -f *.scy *.pdf *.gv

.SUFFIXES: .yml .scy
