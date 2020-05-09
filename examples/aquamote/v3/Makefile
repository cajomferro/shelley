SHELLEYC = shelleyc
SHELLEYV = shelleyv

all: scy pdf

pdf: magnetic.pdf httpclient.pdf wificlient.pdf wifihttp.pdf valve.pdf timer.pdf valvehandlertimer.pdf lowpower-strict.pdf controller.pdf controller-internal-dfa.pdf

scy: controller.scy

wifihttp.scy: wifihttp.yml wificlient.scy httpclient.scy
	time $(SHELLEYC) -d $< -u wificlient.scy\:WiFiClient httpclient.scy\:HTTPClient
	test -f $<

valvehandlertimer.scy: valvehandlertimer.yml valve.scy timer.scy
	time $(SHELLEYC) -d $< -u valve.scy\:Valve timer.scy\:Timer -o $@
	test -f $<

controller.scy: controller.yml valvehandlertimer.scy magnetic.scy wifihttp.scy lowpower-strict.scy
	time $(SHELLEYC) -d $< -i -u magnetic.scy\:Magnetic valvehandlertimer.scy\:ValveHandlerTimer wifihttp.scy\:WiFiHTTP lowpower-strict.scy\:LowPower -o $@
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
