SHELLEYC = shelleyc
SHELLEYV = shelleyv

all: scy

pdf: magnetic.pdf radio.pdf radiosimple.pdf radiosimplest.pdf valve.pdf lowpower-strict.pdf controller.pdf

scy: controller.scy radiosimple.scy

radiosimple.scy: radiosimple.yml radio.scy

radiosimplest.scy: radiosimplest.yml radiosimple.scy

controller.scy: controller.yml valve.scy magnetic.scy radiosimplest.scy lowpower-strict.scy

%.scy: %.yml
	$(SHELLEYC) -u uses.yml -d $< -o $@

%.gv: %.scy
	$(SHELLEYV) $< -o $@

%.pdf: %.gv
	dot -Tpdf -o $@ $<

clean:
	rm -f *.scy *.pdf *.gv


.SUFFIXES: .yml .scy
