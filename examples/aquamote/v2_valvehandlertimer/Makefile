SHELLEYC = shelleyc
SHELLEYV = shelleyv

all: scy pdf

pdf: magnetic.pdf radio.pdf radiosimple.pdf radiosimplest.pdf valve.pdf timer.pdf valvehandlertimer.pdf lowpower-strict.pdf controller.pdf #controller-internal-dfa.pdf controller-internal-nfa.pdf # controller-shuffle-dfa.pdf

scy: controller.scy

radiosimple.scy: radiosimple.yml radio.scy
	$(SHELLEYC) -d $< -u radio.scy\:Radio

radiosimplest.scy: radiosimplest.yml radiosimple.scy
	$(SHELLEYC) -d $< -u radiosimple.scy\:RadioSimple

valvehandlertimer.scy: valvehandlertimer.yml valve.scy timer.scy
	$(SHELLEYC) -d $< -u valve.scy\:Valve timer.scy\:Timer

controller.scy: controller.yml valvehandlertimer.scy magnetic.scy radiosimplest.scy lowpower-strict.scy
	$(SHELLEYC) -d $< -u magnetic.scy\:Magnetic valvehandlertimer.scy\:ValveHandlerTimer radiosimplest.scy\:RadioSimplest lowpower-strict.scy\:LowPower # -i

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
