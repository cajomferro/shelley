include ../common.mk

USES = -u uses.yml

all: scy

pdf: radio_v2.pdf

scy: radio_v2.scy

radio_v2.scy: radio_v2.yml \
	../aquamote_radio_v1/radio_v1.scy \

clean:
	rm -f *.scy *.pdf *.int

.PHONY: all pdf scy
