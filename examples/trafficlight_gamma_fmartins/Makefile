include ../common.mk
USES = -u uses.yml

all: scy

pdf: trafficlightctrl.pdf controller.pdf crossroad.pdf

scy: crossroad.scy

crossroad.scy: crossroad.yml trafficlightctrl.scy controller.scy

clean:
	rm -f *.scy *.pdf *.int

.PHONY: all pdf scy
