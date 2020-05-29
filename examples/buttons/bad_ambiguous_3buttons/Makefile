SHELLEYC = shelleyc
SHELLEYV = shelleyv

all: scy

scy: ambiguous.scy

ambiguous.scy: ambiguous.yml simple_button.scy timer.scy
	# Invalid device: AmbiguousTriggersFailure
	! $(SHELLEYC) -u uses.yml -d $<

%.scy: %.yml
	$(SHELLEYC) -d $<

clean:
	rm -f *.scy *.pdf *.gv