SHELLEYC = shelleyc
SHELLEYV = shelleyv

all: scy

pdf: valve.pdf 1valve.pdf 4valves.pdf 8valves.pdf 9valves.pdf 10valves.pdf 11valves.pdf 12valves.pdf 13valves.pdf # 16valves.pdf 24valves.pdf 32valves.pdf

scy: 1valve.scy 4valves.scy 8valves.scy 9valves.scy 10valves.scy 11valves.scy 12valves.scy 13valves.scy # 16valves.scy 24valves.scy 32valves.scy

valve.scy: valve.yml
	time $(SHELLEYC) -d $< -o valve.scy

%.scy: %.yml valve.scy
	$(SHELLEYC) --dump-timings -d $< -u valve.scy\:Valve -o $@
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
