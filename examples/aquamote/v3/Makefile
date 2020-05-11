SHELLEYC = shelleyc
SHELLEYV = shelleyv

all: scy pdf

internal: scy-internal pdf-internal

pdf: magnetic.pdf httpclient.pdf wificlient.pdf radio.pdf valve.pdf timer.pdf valvehandlertimer.pdf lowpower-strict.pdf controller.pdf

pdf-internal: pdf controller-internal-dfa.pdf controller-internal-nfa.pdf controller-shuffle-dfa.pdf

scy-internal: controller.scy-internal radio.scy valvehandlertimer.scy

scy: controller.scy radio.scy valvehandlertimer.scy

radio.scy: radio.yml wificlient.scy httpclient.scy
	time $(SHELLEYC) -d $< -u wificlient.scy\:WiFiClient httpclient.scy\:HTTPClient
	test -f $<

valvehandlertimer.scy: valvehandlertimer.yml valve.scy timer.scy
	time $(SHELLEYC) -d $< -u valve.scy\:Valve timer.scy\:Timer -o $@
	test -f $<

controller.scy: controller.yml valvehandlertimer.scy magnetic.scy radio.scy lowpower-strict.scy
	time $(SHELLEYC) -d $< -u magnetic.scy\:Magnetic valvehandlertimer.scy\:ValveHandlerTimer radio.scy\:Radio lowpower-strict.scy\:LowPower -o $@
	test -f $<

controller.scy-internal: controller.yml valvehandlertimer.scy magnetic.scy radio.scy lowpower-strict.scy
	time $(SHELLEYC) -d $< -u magnetic.scy\:Magnetic valvehandlertimer.scy\:ValveHandlerTimer radio.scy\:Radio lowpower-strict.scy\:LowPower -o $@ -i -v
	test -f $<

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
