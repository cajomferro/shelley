include ../common.mk
.PHONY: all pdf scy clean all

all: scy

pdf: simple.pdf

scy: ambiguous.scy

ambiguous.scy: ambiguous.yml simple.scy
	# Invalid device: AmbiguousTriggersFailure
	! $(SHELLEYC) -d $< -u uses.yml

clean:
	rm -f *.scy *.pdf *.gv