SHELLEYC = shelleyc
SHELLEYVIZ = shelleyv

all: scy pdf

pdf: magnetic.pdf radio.pdf radiosimple.pdf radiosimplest.pdf valve.pdf timer.pdf valvehandlertimer.pdf valvehandler.pdf lowpower-strict.pdf controller.pdf

scy: controller.scy

radiosimple.scy: radiosimple.yml radio.scy
	$(SHELLEYC) -d $< -u radio.scy\:Radio

radiosimplest.scy: radiosimplest.yml radiosimple.scy
	$(SHELLEYC) -d $< -u radiosimple.scy\:RadioSimple

valvehandlertimer.scy: valvehandlertimer.yml valve.scy timer.scy
	$(SHELLEYC) -d $< -u valve.scy\:Valve timer.scy\:Timer

valvehandler.scy: valvehandler.yml valvehandlertimer.scy
	$(SHELLEYC) -d $< -u valvehandlertimer.scy\:ValveHandlerTimer

controller.scy: controller.yml valvehandler.scy magnetic.scy radiosimplest.scy lowpower-strict.scy
	$(SHELLEYC) -d $< -u magnetic.scy\:Magnetic valvehandler.scy\:ValveHandler radiosimplest.scy\:RadioSimplest lowpower-strict.scy\:LowPower

%.scy: %.yml
	$(SHELLEYC) -d $< -o $@
	test -f $<

%.gv: %.scy
	$(SHELLEYVIZ) $< -o $@

%.pdf: %.gv
	dot -Tpdf -o $@ $<

clean:
	rm -f *.scy *.pdf *.gv


.SUFFIXES: .yml .scy
