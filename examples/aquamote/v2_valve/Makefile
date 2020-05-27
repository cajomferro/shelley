SHELLEYC = shelleyc
SHELLEYV = shelleyv

all: scy

pdf: magnetic.pdf radio.pdf radiosimple.pdf radiosimplest.pdf valve.pdf lowpower-strict.pdf controller.pdf

scy: controller.scy radiosimple.scy

radiosimple.scy: radiosimple.yml radio.scy
	$(SHELLEYC) -d $< -u radio.scy\:Radio

radiosimplest.scy: radiosimplest.yml radiosimple.scy
	$(SHELLEYC) -d $< -u radiosimple.scy\:RadioSimple

controller.scy: controller.yml valve.scy magnetic.scy radiosimplest.scy lowpower-strict.scy
	$(SHELLEYC) -d $< -u magnetic.scy\:Magnetic valve.scy\:Valve radiosimplest.scy\:RadioSimplest lowpower-strict.scy\:LowPower

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
