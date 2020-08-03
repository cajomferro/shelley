include ../common.mk

all: scy

pdf: aquamote_core.pdf aquamote_core_v2.pdf aquamote_core_v3.pdf

scy: aquamote_core.scy aquamote_core_v2.scy aquamote_core_v3.scy

USES = -u uses.yml

aquamote_core.scy: aquamote_core.yml \
	../aquamote_controller/controller_radioclient_v2.scy

aquamote_core_v3.scy: aquamote_core_v3.yml \
	../base/timer.scy \
	../aquamote_valve/valve.scy \
	../aquamote_valvehandlertimer/valvehandlertimer.scy \
	../aquamote_magnetic/magnetic.scy \
	../aquamote_radio_client_v2/httpclient.scy \
	../aquamote_radio_client_v2/gprsclient.scy \
	../aquamote_lowpower/lowpower-strict.scy \

clean:
	rm -f *.scy *.pdf *.gv

.PHONY: all pdf scy
