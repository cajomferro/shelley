SHELLEYC = shelleyc
SHELLEYV = shelleyv

all: scy

pdf: 4valves_seq.pdf 4valves_xor.pdf 4valves_seqx25.pdf 4valves_xorx25.pdf 4valves_seqx50.pdf 4valves_xorx50.pdf

scy: 4valves_seq.scy 4valves_xor.scy 4valves_seqx25.scy 4valves_xorx25.scy 4valves_seqx50.scy 4valves_xorx50.scy

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
