include ../common.mk
.PHONY: all pdf scy clean all

all: scy

pdf: button.pdf

scy: trigger_undeclared.scy

trigger_undeclared.scy: trigger_undeclared.yml ../base/button.scy
	# Shelley parser error: Events declared not used in behavior: '{'off'}'
	! $(SHELLEYC) $(USES) -d $<

clean:
	rm -f *.scy *.pdf *.gv