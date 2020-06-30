include ../common.mk

all: scy

pdf: controller_v1.pdf controller_v2.pdf controller_v2_finalstates.pdf

scy: controller_v1.scy controller_v2.scy controller_v2_finalstates.scy

USES = -u uses.yml

controller_v1.scy: controller_v1.yml \
	../aquamote_valve/valve.scy \
	../aquamote_magnetic/magnetic.scy \
	../aquamote_radio_v1 \
	../aquamote_lowpower/lowpower.scy

controller_v2.scy: controller_v2.yml \
	../aquamote_valve/valve.scy \
	../aquamote_magnetic/magnetic.scy \
	../aquamote_radio_v1 \
	../aquamote_lowpower/lowpower-strict.scy

controller_v2_finalstates.scy: controller_v2.yml \
	../aquamote_valve/valve.scy \
	../aquamote_magnetic/magnetic.scy \
	../aquamote_radio_v1 \
	../aquamote_lowpower/lowpower-strict-finalstates.scy

#
#controller.scy: controller.yml \
#	valve.scy \
#	../aquamote_v1/magnetic.scy \
#	../aquamote_v2_valve/radiosimplest.scy \
#	../aquamote_v2/lowpower-strict.scy

clean:
	rm -f *.scy *.pdf *.gv

.PHONY: all pdf scy
