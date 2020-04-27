SHELLEYC = shelleyc
SHELLEYVIZ = shelleyv

all: scy pdf

pdf: simple.pdf

scy: ambiguous.scy

ambiguous.scy: ambiguous.yml simple.scy
	# Invalid device: AmbiguousTriggersFailure
	! $(SHELLEYC) -d $< -u simple.scy\:SimpleButton

%.scy: %.yml
	$(SHELLEYC) -d $<

%.gv: %.scy
	$(SHELLEYVIZ) $< -o $@

%.pdf: %.gv
	dot -Tpdf -o $@ $<

clean:
	rm -f *.scy *.pdf *.gv