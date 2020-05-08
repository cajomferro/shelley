SHELLEYC = shelleyc
SHELLEYV = shelleyv

all: scy pdf

pdf: magnetic.pdf radio.pdf radiosimple.pdf radiosimplest.pdf valve.pdf timer.pdf valvehandlertimer.pdf lowpower-strict.pdf controller.pdf

scy: controller.scy

radiosimple.scy: radiosimple.yml radio.scy
	$(SHELLEYC) -d $< -u radio.scy\:Radio -o $@

radiosimplest.scy: radiosimplest.yml radiosimple.scy
	$(SHELLEYC) -d $< -u radiosimple.scy\:RadioSimple -o $@

valvehandlertimer.scy: valvehandlertimer.yml valve.scy timer.scy
	$(SHELLEYC) -d $< -u valve.scy\:Valve timer.scy\:Timer -o $@

controller.scy: controller.yml valvehandlertimer.scy magnetic.scy radiosimplest.scy lowpower-strict.scy
	$(SHELLEYC) -d $< -u magnetic.scy\:Magnetic valvehandlertimer.scy\:ValveHandlerTimer radiosimplest.scy\:RadioSimplest lowpower-strict.scy\:LowPower -o $@

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
