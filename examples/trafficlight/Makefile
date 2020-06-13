include ../common.mk

all: scy

pdf: control.pdf controller.pdf led.pdf lightcommands.pdf policeinterrupt.pdf timer.pdf trafficlight.pdf

scy: crossroad.scy controller.scy trafficlight.scy

controller.scy: controller.yml timer.scy control.scy policeinterrupt.scy

crossroad.scy: crossroad.yml controller.scy trafficlight.scy

clean:
	rm -f *.scy *.pdf *.int

.PHONY: all pdf scy

.SUFFIXES: .yml .scy .int
