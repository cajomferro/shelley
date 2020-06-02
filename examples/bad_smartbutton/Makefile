SHELLEYC = shelleyc
SHELLEYV = shelleyv

all: scy

pdf: button.pdf

scy: smartbutton.scy

smartbutton.scy: smartbutton.yml button.scy
	# Invalid device: TriggerIntegrationFailure(micro_trace=('b.pressed', 'b.pressed'), macro_trace=('on',), component_errors={'b': (('pressed', 'pressed'), 1)})
	! $(SHELLEYC) -d $< -u uses.yml

%.scy: %.yml
	$(SHELLEYC) -d $<

%.gv: %.scy
	$(SHELLEYV) $< -o $@

%.pdf: %.gv
	dot -Tpdf -o $@ $<

clean:
	rm -f *.scy *.pdf *.gv