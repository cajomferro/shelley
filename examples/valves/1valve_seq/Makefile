SHELLEYC = shelleyc
SHELLEYV = shelleyv

all: scy

pdf: valve.pdf valve_seq.pdf valve_2seq.pdf valve_3seq.pdf

scy: valve.scy valve_seq.scy valve_2seq.scy valve_3seq.scy

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
