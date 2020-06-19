include ../common.mk
.PHONY: all pdf scy clean all

all: scy

pdf: simple.pdf

scy: ambiguous.scy

ambiguous.scy: ambiguous.yml ../base/simple_button.scy
	# Invalid device: AmbiguousTriggersFailure
	! $(SHELLEYC) $(USES) -d $<

clean:
	rm -f *.scy *.pdf *.gv