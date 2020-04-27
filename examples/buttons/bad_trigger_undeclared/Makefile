SHELLEYC = shelleyc
SHELLEYVIZ = shelleyv

all: scy pdf

pdf: singleclick.pdf

scy: trigger_undeclared.scy

trigger_undeclared.scy: trigger_undeclared.yml singleclick.scy
	# Shelley parser error: Trigger event 'off' has not been declared
	! $(SHELLEYC) -d $< -u singleclick.scy\:SingleClickButton

%.scy: %.yml
	$(SHELLEYC) -d $<

%.gv: %.scy
	$(SHELLEYVIZ) $< -o $@

%.pdf: %.gv
	dot -Tpdf -o $@ $<

clean:
	rm -f *.scy *.pdf *.gv