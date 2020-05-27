SHELLEYC = shelleyc
SHELLEYV = shelleyv

all: scy

pdf: magnetic.pdf radio.pdf radiosimple.pdf radiosimplest.pdf valve.pdf valvehandler.pdf lowpower-strict.pdf controller.pdf

scy: controller.scy radiosimple.scy valvehandler.scy

radiosimple.scy: radiosimple.yml radio.scy
	$(SHELLEYC) -d $< -u radio.scy\:Radio

radiosimplest.scy: radiosimplest.yml radiosimple.scy
	$(SHELLEYC) -d $< -u radiosimple.scy\:RadioSimple

valvehandler.scy: valvehandler.yml valve.scy
	$(SHELLEYC) -d $< -u valve.scy\:Valve

controller.scy: controller.yml valvehandler.scy magnetic.scy radiosimplest.scy lowpower-strict.scy
	$(SHELLEYC) -d $< -u magnetic.scy\:Magnetic valvehandler.scy\:ValveHandler radiosimplest.scy\:RadioSimplest lowpower-strict.scy\:LowPower

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
