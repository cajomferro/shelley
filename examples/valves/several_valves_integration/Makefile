SHELLEYC = shelleyc
SHELLEYV = shelleyv

all: scy

pdf: valve.pdf 4valves.pdf 8valves.pdf 2x4valves.pdf 3x4valves.pdf 8x4valves.pdf 4x2x4valves.pdf 12valves.pdf 13valves.pdf 16valves.pdf # 24valves.pdf 32valves.pdf

scy: 4valves.scy 8valves.scy 2x4valves.scy 3x4valves.scy 8x4valves.scy 4x2x4valves.scy 12valves.scy 13valves.scy 16valves.scy # 24valves.scy 32valves.scy

%.scy: %.yml valve.scy
	$(SHELLEYC) -d $< -u valve.scy\:Valve

2x4valves.scy: 2x4valves.yml 4valves.scy
	$(SHELLEYC) -d $< -u 4valves.scy\:ValveHandler

3x4valves.scy: 3x4valves.yml 4valves.scy
	$(SHELLEYC) -d $< -u 4valves.scy\:ValveHandler

8x4valves.scy: 8x4valves.yml 4valves.scy
	$(SHELLEYC) -d $< -u 4valves.scy\:ValveHandler

4x2x4valves.scy: 4x2x4valves.yml 2x4valves.scy
	$(SHELLEYC) -d $< -u 2x4valves.scy\:SuperValveHandler

valve.scy: valve.yml
	$(SHELLEYC) -d $< -o $@
	test -f $<

%.gv: %.scy
	$(SHELLEYV) $< -o $@

%.pdf: %.gv
	dot -Tpdf -o $@ $<

clean:
	rm -f *.scy *.pdf *.gv


.SUFFIXES: .yml .scy
