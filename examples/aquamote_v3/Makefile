include ../common.mk

all: scy

pdf: magnetic.pdf httpclient.pdf wificlient.pdf radio.pdf valve.pdf timer.pdf valvehandlertimer.pdf lowpower-strict.pdf controller.pdf

scy: controller.scy

radio.scy: radio.yml wificlient.scy httpclient.scy

USES = -u uses.yml

../aquamote_v2_valvehandlertimer/valvehandlertimer.scy: \
	../aquamote_v2_valvehandlertimer/valvehandlertimer.yml \
	../aquamote_v1/valve.scy \
	../base/timer.scy

controller.scy: controller.yml \
	../aquamote_v2_valvehandlertimer/valvehandlertimer.scy \
	../aquamote_v1/magnetic.scy \
	radio.scy \
	../aquamote_v2/lowpower-strict.scy

clean:
	rm -f *.scy *.pdf *.int

.PHONY: all pdf scy
