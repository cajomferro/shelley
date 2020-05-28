SHELLEYC = shelleyc
SHELLEYV = shelleyv

all: scy

pdf: magnetic.pdf radio.pdf valve.pdf lowpower-strict.pdf controller.pdf

scy: controller.scy

controller.scy: controller.yml valve.scy magnetic.scy radio.scy lowpower-strict.scy

%.scy: %.yml
	$(SHELLEYC) -u uses.yml -d $< -o $@

%.gv: %.scy
	$(SHELLEYV) $< -o $@

%.pdf: %.gv
	dot -Tpdf -o $@ $<

clean:
	rm -f *.scy *.pdf *.gv


.SUFFIXES: .yml .scy
