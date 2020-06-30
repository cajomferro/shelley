include ../common.mk

all: scy

pdf: controller_radio_v1.pdf \
	controller_finalstates.pdf \
	controller_radio_v1_lp_strict.pdf \
	controller_radio_v3_lp_strict.pdf \
	controller_valvehandler.pdf \
	controller_valvehandlertimer.pdf \
	controller_radioclient.pdf \
	controller_radioclient_v2.pdf

scy: controller_radio_v1.scy \
	controller_finalstates.scy \
	controller_radio_v1_lp_strict.scy \
	controller_radio_v3_lp_strict.scy \
	controller_valvehandler.scy \
	controller_valvehandlertimer.scy \
	controller_radioclient.scy \
	controller_radioclient_v2.scy

USES = -u uses.yml

controller_finalstates.scy: controller_finalstates.yml \
	../aquamote_valve/valve.scy \
	../aquamote_magnetic/magnetic.scy \
	../aquamote_radio_simple/radio_finalstates.scy \
	../aquamote_lowpower/lowpower-strict-finalstates.scy

controller_radio_v1.scy: controller_radio_v1.yml \
	../aquamote_valve/valve.scy \
	../aquamote_magnetic/magnetic.scy \
	../aquamote_radio_simple/radio_v1.scy \
	../aquamote_lowpower/lowpower.scy

# similiar as before but using a strict lowpower module
controller_radio_v1_lp_strict.scy: controller_radio_v1_lp_strict.yml \
	../aquamote_valve/valve.scy \
	../aquamote_magnetic/magnetic.scy \
	../aquamote_radio_simple/radio_v1.scy \
	../aquamote_lowpower/lowpower-strict.scy

# radio_v3 (simpler) uses radio_v2 uses radio_v1 (more complex)
controller_radio_v3_lp_strict.scy: controller_radio_v3_lp_strict.yml \
	../aquamote_valve/valve.scy \
	../aquamote_magnetic/magnetic.scy \
	../aquamote_radio_simple/radio_v1.scy \
	../aquamote_radio_simple/radio_v2.scy \
	../aquamote_radio_simple/radio_v3.scy \
	../aquamote_lowpower/lowpower-strict.scy

# use a valve handler without timer
controller_valvehandler.scy: controller_valvehandler.yml \
	../aquamote_valve/valve.scy \
	../aquamote_valvehandler/valvehandler.scy \
	../aquamote_magnetic/magnetic.scy \
	../aquamote_radio_simple/radio_v1.scy \
	../aquamote_radio_simple/radio_v2.scy \
	../aquamote_radio_simple/radio_v3.scy \
	../aquamote_lowpower/lowpower-strict.scy

# use a valve handler with timer
controller_valvehandlertimer.scy: controller_valvehandlertimer.yml \
	../base/timer.scy \
	../aquamote_valve/valve.scy \
	../aquamote_valvehandlertimer/valvehandlertimer.scy \
	../aquamote_magnetic/magnetic.scy \
	../aquamote_radio_simple/radio_v1.scy \
	../aquamote_radio_simple/radio_v2.scy \
	../aquamote_radio_simple/radio_v3.scy \
	../aquamote_lowpower/lowpower-strict.scy \

controller_radioclient.scy: controller_radioclient.yml \
	../base/timer.scy \
	../aquamote_valve/valve.scy \
	../aquamote_valvehandlertimer/valvehandlertimer.scy \
	../aquamote_magnetic/magnetic.scy \
	../aquamote_radio_client/httpclient.scy \
	../aquamote_radio_client/wificlient.scy \
	../aquamote_radio_client/radioclient.scy \
	../aquamote_lowpower/lowpower-strict.scy \

# same as before but handling radioclient error cases
controller_radioclient_v2.scy: controller_radioclient_v2.yml \
	../base/timer.scy \
	../aquamote_valve/valve.scy \
	../aquamote_valvehandlertimer/valvehandlertimer.scy \
	../aquamote_magnetic/magnetic.scy \
	../aquamote_radio_client/httpclient.scy \
	../aquamote_radio_client/wificlient.scy \
	../aquamote_radio_client/radioclient.scy \
	../aquamote_lowpower/lowpower-strict.scy \

clean:
	rm -f *.scy *.pdf *.gv

.PHONY: all pdf scy
