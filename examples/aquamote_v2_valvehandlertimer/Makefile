SHELLEYC = shelleyc
SHELLEYV = shelleyv

all: scy

pdf: magnetic.pdf radio.pdf radiosimple.pdf radiosimplest.pdf valve.pdf timer.pdf valvehandlertimer.pdf lowpower-strict.pdf controller.pdf #controller-internal-dfa.pdf controller-internal-nfa.pdf # controller-shuffle-dfa.pdf

scy: controller.scy

radiosimple.scy: radiosimple.yml radio.scy

radiosimplest.scy: radiosimplest.yml radiosimple.scy

valvehandlertimer.scy: valvehandlertimer.yml valve.scy timer.scy

controller.scy: controller.yml valvehandlertimer.scy magnetic.scy radiosimplest.scy lowpower-strict.scy

%.scy: %.yml
	$(SHELLEYC) -u uses.yml -d $< -o $@

%.gv: %.scy
	$(SHELLEYV) $< -o $@

%.pdf: %.gv
	dot -Tpdf -o $@ $<

clean:
	rm -f *.scy *.pdf *.gv


.SUFFIXES: .yml .scy
