SHELLEYC = shelleyc
SHELLEYV = shelleyv

all: scy

pdf: button.pdf

scy: trigger_undeclared.scy

trigger_undeclared.scy: trigger_undeclared.yml button.scy
	# Shelley parser error: Events declared not used in behavior: '{'off'}'
	! $(SHELLEYC) -d $< -u uses.yml

%.scy: %.yml
	$(SHELLEYC) -d $<

%.gv: %.scy
	$(SHELLEYV) $< -o $@

%.pdf: %.gv
	dot -Tpdf -o $@ $<

clean:
	rm -f *.scy *.pdf *.gv