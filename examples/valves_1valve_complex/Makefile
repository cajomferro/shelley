SHELLEYC = shelleyc
SHELLEYV = shelleyv

all: scy

pdf: valve.pdf valve_macro.pdf valve_macro2.pdf valve_macro3.pdf # valve_macro4.pdf TOO SLOW!

scy: valve.scy valve_macro.scy valve_macro2.scy valve_macro3.scy # valve_macro4.scy TOO SLOW!

valve.scy: valve.yml
	$(SHELLEYC) -d $< -u uses.yml -o $@

%.scy: %.yml valve.scy
	$(SHELLEYC) -d $< -u uses.yml -o $@

%.gv: %.scy
	$(SHELLEYV) $< -o $@

%.pdf: %.gv
	dot -Tpdf -o $@ $<

clean:
	rm -f *.scy *.pdf *.gv


.SUFFIXES: .yml .scy
