include ../common.mk

all: scy

pdf: control.pdf timer.pdf policeinterrupt.pdf lightcommands.pdf trafficlightctrl.pdf

scy: trafficlightctrl.scy

trafficlightctrl.scy: trafficlightctrl.yml timer.scy control.scy policeinterrupt.scy lightcommands.scy

clean:
	rm -f *.scy *.pdf *.int

.PHONY: all pdf scy
