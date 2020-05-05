SHELLEYC = shelleyc
SHELLEYV = shelleyv

all: scy pdf

pdf: valve.pdf 1valve_xor.pdf 4valves_xor.pdf 8valves_xor.pdf 9valves_xor.pdf 10valves_xor.pdf 11valves_xor.pdf 12valves_xor.pdf 13valves_xor.pdf # 16valves_xor.pdf 24valves_xor.pdf 32valves_xor.pdf

scy: 1valve_xor.scy 4valves_xor.scy 8valves_xor.scy 9valves_xor.scy 10valves_xor.scy 11valves_xor.scy 12valves_xor.scy 13valves_xor.scy # 16valves_xor.scy 24valves_xor.scy 32valves_xor.scy

valve.scy: valve.yml
	time $(SHELLEYC) -d $< -o valve.scy

%.scy: %.yml valve.scy
	time $(SHELLEYC) -d $< -u valve.scy\:Valve -o $@
	test -f $<

%.gv: %.scy
	$(SHELLEYV) $< -o $@

%.pdf: %.gv
	dot -Tpdf -o $@ $<

clean:
	rm -f *.scy *.pdf *.gv


.SUFFIXES: .yml .scy
