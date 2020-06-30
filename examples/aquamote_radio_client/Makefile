include ../common.mk

all: scy

pdf: httpclient.pdf wificlient.pdf radio.pdf

scy: radio.scy

radio.scy: radio.yml wificlient.scy httpclient.scy

USES = -u uses.yml

clean:
	rm -f *.scy *.pdf *.int

.PHONY: all pdf scy
