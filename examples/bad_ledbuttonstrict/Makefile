SHELLEYC = shelleyc
SHELLEYV = shelleyv

all: scy

pdf: simple_button.pdf led_strict.pdf

scy: ledbutton.scy

ledbutton.scy: ledbutton.yml simple_button.scy led_strict.scy
	# Invalid device: TriggerIntegrationFailure(micro_trace=('b1.pressed', 'led1.on', 'b1.pressed', 'led1.on'), macro_trace=('led1', 'led1'), component_errors={'led1': (('on', 'on'), 1)})
	! $(SHELLEYC) -d $< -u uses.yml

%.scy: %.yml
	$(SHELLEYC) -d $<

%.gv: %.scy
	$(SHELLEYV) $< -o $@

%.pdf: %.gv
	dot -Tpdf -o $@ $<

clean:
	rm -f *.scy *.pdf *.gv

.SUFFIXES: .yml .scy
