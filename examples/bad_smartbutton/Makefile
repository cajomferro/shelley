include ../common.mk
.PHONY: all pdf scy clean all

all: scy

pdf: button.pdf

scy: smartbutton.scy

smartbutton.scy: smartbutton.yml ../base/button.scy
	# Invalid device: TriggerIntegrationFailure(micro_trace=('b.pressed', 'b.pressed'), macro_trace=('on',), component_errors={'b': (('pressed', 'pressed'), 1)})
	! $(SHELLEYC) $(USES) -d $<

clean:
	rm -f *.scy *.pdf *.gv