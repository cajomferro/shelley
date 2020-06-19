include ../common.mk
.PHONY: all pdf scy clean all

all: scy

pdf: simple_button.pdf led_strict.pdf

scy: ledbutton.scy

ledbutton.scy: ledbutton.yml ../base/simple_button.scy ../base/led_strict.scy
	# Invalid device: TriggerIntegrationFailure(micro_trace=('b1.pressed', 'led1.on', 'b1.pressed', 'led1.on'), macro_trace=('led1', 'led1'), component_errors={'led1': (('on', 'on'), 1)})
	! $(SHELLEYC) $(USES) -d $<

clean:
	rm -f *.scy *.pdf *.gv
