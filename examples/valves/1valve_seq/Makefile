SHELLEYC = shelleyc
SHELLEYV = shelleyv

all: scy

pdf: valve.pdf valve_seq.pdf valve_2seq.pdf valve_3seq.pdf

scy: valve.scy valve_seq.scy valve_2seq.scy valve_3seq.scy

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
