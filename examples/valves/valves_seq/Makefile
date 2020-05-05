SHELLEYC = shelleyc
SHELLEYV = shelleyv

all: scy pdf

pdf: valve.pdf 1valve_seq.pdf 4valves_seq.pdf 8valves_seq.pdf 9valves_seq.pdf 10valves_seq.pdf 11valves_seq.pdf 12valves_seq.pdf 13valves_seq.pdf 4valves_seqx200.pdf # 16valves_seq.pdf 24valves_seq.pdf 32valves_seq.pdf

scy: 1valve_seq.scy 4valves_seq.scy 8valves_seq.scy 9valves_seq.scy 10valves_seq.scy 11valves_seq.scy 12valves_seq.scy 13valves_seq.scy 4valves_seqx200.scy # 16valves_seq.scy 24valves_seq.scy 32valves_seq.scy

valve.scy: valve.yml
	time $(SHELLEYC) -d $< -o valve.scy

%.scy: %.yml valve.scy
	time $(SHELLEYC) -d $< -u valve.scy\:Valve -o $@
	test -f $<

%.scy: %.yml
	$(SHELLEYC) -d $< -o $@
	test -f $<

%.gv: %.scy
	$(SHELLEYV) $< -o $@

%.pdf: %.gv
	dot -Tpdf -o $@ $<

clean:
	rm -f *.scy *.pdf *.gv


.SUFFIXES: .yml .scy
