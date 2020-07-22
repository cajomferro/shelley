include ../common.mk

all: scy

pdf: trafficlight.pdf traffic-ctl.pdf crossroad.pdf

scy: crossroad.scy

traffic-ctl.scy: traffic-ctl.yml trafficlight.scy

crossroad.scy: crossroad.yml traffic-ctl.scy trafficlight.scy

trafficlight.scy: trafficlight.yml

USES = -u uses.yml

clean:
	rm -f *.scy *.pdf *.int

.PHONY: all pdf scy
