SHELLEYC = shelleyc
SHELLEYV = shelleyv

all: scy pdf

pdf: singleclick.pdf

scy: missing_trigger.scy

missing_trigger.scy: missing_trigger.yml singleclick.scy
	# Shelley parser error: Missing trigger for event 'off'
	! $(SHELLEYC) -d $< -u singleclick.scy\:SingleClickButton

%.scy: %.yml
	$(SHELLEYC) -d $<

%.gv: %.scy
	$(SHELLEYV) $< -o $@

%.pdf: %.gv
	dot -Tpdf -o $@ $<

clean:
	rm -f *.scy *.pdf *.gv