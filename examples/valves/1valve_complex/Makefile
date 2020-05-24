SHELLEYC = shelleyc
SHELLEYV = shelleyv

all: scy

pdf: valve.pdf valve_macro.pdf valve_macro2.pdf valve_macro3.pdf valve_macro4.pdf

scy: valve.scy valve_macro.scy valve_macro2.scy valve_macro3.scy valve_macro4.scy

valve.scy: valve.yml
	$(SHELLEYC) -d $< -o valve.scy

%.scy: %.yml valve.scy
	$(SHELLEYC) -d $< -u valve.scy\:Valve -o $@
	test -f $<

%.gv: %.scy
	$(SHELLEYV) $< -o $@

%.pdf: %.gv
	dot -Tpdf -o $@ $<

clean:
	rm -f *.scy *.pdf *.gv


.SUFFIXES: .yml .scy
