SHELLEYC = shelleyc
SHELLEYV = shelleyv

all: scy pdf

pdf: httpclient.pdf wificlient.pdf wifihttp.pdf

scy: wifihttp.scy

wifihttp.scy: wifihttp.yml wificlient.scy httpclient.scy
	$(SHELLEYC) -d $< -u wificlient.scy\:WiFiClient httpclient.scy\:HTTPClient

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
