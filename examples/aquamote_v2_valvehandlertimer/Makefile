include ../common.mk

all: scy

pdf: magnetic.pdf radio.pdf radiosimple.pdf radiosimplest.pdf valve.pdf timer.pdf valvehandlertimer.pdf lowpower-strict.pdf controller.pdf #controller-internal-dfa.pdf controller-internal-nfa.pdf # controller-shuffle-dfa.pdf

scy: controller.scy

USES = -u uses.yml

radiosimplest.scy: radiosimplest.yml radiosimple.scy

valvehandlertimer.scy: \
	valvehandlertimer.yml \
	../aquamote_v1/valve.scy \
	../base/timer.scy

controller.scy: controller.yml \
	valvehandlertimer.scy \
	../aquamote_v1/magnetic.scy \
	../aquamote_v2_valve/radiosimplest.scy \
	../aquamote_v2/lowpower-strict.scy

clean:
	rm -f *.scy *.pdf *.gv


.PHONY: all pdf scy clean all
