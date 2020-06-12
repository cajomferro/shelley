include ../common.mk

all: scy

pdf: control.pdf controller.pdf led.pdf light_commands.pdf police_interrupt.pdf timer.pdf trafficlight.pdf

scy: crossroad.scy controller.scy trafficlight.scy

crossroad.scy: crossroad.yml controller.scy trafficlight.scy

clean:
	rm -f *.scy *.pdf *.int

.PHONY: all pdf scy

.SUFFIXES: .yml .scy .int
