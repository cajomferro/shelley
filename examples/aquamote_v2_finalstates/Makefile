include ../common.mk

all: scy

pdf: magnetic.pdf radio.pdf valve.pdf lowpower-strict.pdf controller.pdf

scy: controller.scy

USES = -u uses.yml

controller.scy: controller.yml \
	../aquamote_v1/valve.scy \
	../aquamote_v1/magnetic.scy \
	radio.scy \
	lowpower-strict.scy

clean:
	rm -f *.scy *.pdf *.gv

.PHONY: all pdf scy
