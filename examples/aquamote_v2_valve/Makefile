include ../common.mk

all: scy

pdf: magnetic.pdf radio.pdf radiosimple.pdf radiosimplest.pdf valve.pdf lowpower-strict.pdf controller.pdf

scy: controller.scy radiosimple.scy

radiosimple.scy: radiosimple.yml ../aquamote_v1/radio.scy

radiosimplest.scy: radiosimplest.yml radiosimple.scy

USES = -u uses.yml

controller.scy: controller.yml \
	../aquamote_v1/valve.scy \
	../aquamote_v1/magnetic.scy \
	radiosimplest.scy \
	../aquamote_v2/lowpower-strict.yml

clean:
	rm -f *.scy *.pdf *.gv

.PHONY: all pdf scy
