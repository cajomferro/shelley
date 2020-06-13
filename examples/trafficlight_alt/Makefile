include ../common.mk

all: scy

pdf: light.pdf traffic-ctl.pdf crossroad.pdf

scy: crossroad.scy

traffic-ctl.scy: light.scy

crossroad.scy: traffic-ctl.scy

clean:
	rm -f *.scy *.pdf *.int

.PHONY: all pdf scy
