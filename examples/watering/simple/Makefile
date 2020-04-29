SHELLEYC = shelleyc
SHELLEYVIZ = shelleyv

all: scy pdf

pdf: magnetic.pdf radio.pdf valve.pdf lowpower.pdf controller.pdf

scy: controller.scy

controller.scy: controller.yml valve.scy magnetic.scy radio.scy lowpower.scy
	$(SHELLEYC) -d $< -u magnetic.scy\:Magnetic valve.scy\:Valve radio.scy\:Radio lowpower.scy\:LowPower

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
