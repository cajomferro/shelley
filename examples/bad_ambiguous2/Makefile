include ../common.mk
.PHONY: all pdf scy clean all

all: scy

pdf: singleclick.pdf timer.pdf

scy: ambiguous.scy

ambiguous.scy: ambiguous.yml singleclick.scy timer.scy
	# Invalid device: AmbiguousTriggersFailure
	! $(SHELLEYC) -u uses.yml -d $<

clean:
	rm -f *.scy *.pdf *.gv