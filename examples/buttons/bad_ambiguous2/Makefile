SHELLEYC = shelleyc
SHELLEYV = shelleyv

all: scy pdf

pdf: singleclick.pdf timer.pdf

scy: ambiguous.scy

ambiguous.scy: ambiguous.yml singleclick.scy timer.scy
	# Invalid device: AmbiguousTriggersFailure
	! $(SHELLEYC) -d $< -u singleclick.scy\:SingleClickButton timer.scy\:Timer

%.scy: %.yml
	$(SHELLEYC) -d $<

%.gv: %.scy
	$(SHELLEYV) $< -o $@

%.pdf: %.gv
	dot -Tpdf -o $@ $<

clean:
	rm -f *.scy *.pdf *.gv