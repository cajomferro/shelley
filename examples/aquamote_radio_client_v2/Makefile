include ../common.mk

all: scy

pdf: httpclient.pdf wificlient.pdf radioclient.pdf

scy: radioclient.scy

radioclient.scy: radioclient.yml wificlient.scy httpclient.scy

USES = -u uses.yml

clean:
	rm -f *.scy *.pdf *.int

.PHONY: all pdf scy
