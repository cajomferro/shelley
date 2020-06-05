include ../common.mk
.PHONY: all pdf scy clean all

all: scy

scy: ambiguous.scy

ambiguous.scy: ambiguous.yml simple_button.scy timer.scy
	# Invalid device: AmbiguousTriggersFailure
	! $(SHELLEYC) -u uses.yml -d $< -o $@

clean:
	rm -f *.scy *.pdf