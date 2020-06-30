include ../common.mk

USES = -u uses.yml

all: scy

pdf: radio_v1.pdf radio_v2.pdf radio_v3.pdf

scy: radio_v3.scy

radio_v1.scy: radio_v1.yml

radio_v2.scy: radio_v2.yml radio_v1.scy

radio_v3.scy: radio_v3.yml radio_v2.scy

clean:
	rm -f *.scy *.pdf *.int

.PHONY: all pdf scy
