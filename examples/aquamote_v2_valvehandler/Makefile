SHELLEYC = shelleyc
SHELLEYV = shelleyv

all: scy

pdf: magnetic.pdf radio.pdf radiosimple.pdf radiosimplest.pdf valve.pdf valvehandler.pdf lowpower-strict.pdf controller.pdf

scy: controller.scy radiosimple.scy valvehandler.scy

radiosimple.scy: radiosimple.yml radio.scy

radiosimplest.scy: radiosimplest.yml radiosimple.scy

valvehandler.scy: valvehandler.yml valve.scy

controller.scy: controller.yml valvehandler.scy magnetic.scy radiosimplest.scy lowpower-strict.scy

%.scy: %.yml
	$(SHELLEYC) -u uses.yml -d $< -o $@

%.gv: %.scy
	$(SHELLEYV) $< -o $@

%.pdf: %.gv
	dot -Tpdf -o $@ $<

clean:
	rm -f *.scy *.pdf *.gv


.SUFFIXES: .yml .scy
