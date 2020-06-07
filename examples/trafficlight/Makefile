include ../common.mk

all: scy

pdf: led.pdf timer.pdf trafficlight.pdf controller.pdf

scy: controller.scy

trafficlight.scy: led.scy

controller.scy: controller.yml trafficlight.scy timer.scy

clean:
	rm -f *.scy *.pdf *.int

.PHONY: all pdf scy

.SUFFIXES: .yml .scy .int
