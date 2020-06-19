include ../common.mk
.PHONY: all pdf scy clean all

all: scy

pdf: button.pdf

scy: missing_trigger.scy

missing_trigger.scy: missing_trigger.yml ../base/button.scy
	# Shelley parser error: Event 'off' doesn't specify micro behavior but device has components!
	! $(SHELLEYC) $(USES) -d $<

clean:
	rm -f *.scy *.pdf *.gv