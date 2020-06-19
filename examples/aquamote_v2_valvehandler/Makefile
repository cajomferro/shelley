include ../common.mk

all: scy

pdf: magnetic.pdf radio.pdf radiosimple.pdf radiosimplest.pdf valve.pdf valvehandler.pdf lowpower-strict.pdf controller.pdf

scy: controller.scy

USES = -u uses.yml

../aquamote_v2_valve/radiosimple.scy: ../aquamote_v1/radio.scy

../aquamote_v2_valve/radiosimplest.scy: ../aquamote_v2_valve/radiosimplest.yml ../aquamote_v2_valve/radiosimple.scy

valvehandler.scy: valvehandler.yml ../aquamote_v1/valve.scy

controller.scy: controller.yml \
	valvehandler.scy \
	../aquamote_v1/magnetic.scy \
	../aquamote_v2_valve/radiosimplest.scy \
	../aquamote_v2/lowpower-strict.scy

clean:
	rm -f *.scy *.pdf *.gv

.PHONY: all pdf scy
