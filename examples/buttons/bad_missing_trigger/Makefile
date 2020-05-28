SHELLEYC = shelleyc
SHELLEYV = shelleyv

all: scy

pdf: button.pdf

scy: missing_trigger.scy

missing_trigger.scy: missing_trigger.yml button.scy
	# Shelley parser error: Event 'off' doesn't specify micro behavior but device has components!
	! $(SHELLEYC) -d $< -u uses.yml

%.scy: %.yml
	$(SHELLEYC) -d $<

%.gv: %.scy
	$(SHELLEYV) $< -o $@

%.pdf: %.gv
	dot -Tpdf -o $@ $<

clean:
	rm -f *.scy *.pdf *.gv