include ../common.mk

all: scy

pdf: control.pdf timer.pdf policeinterrupt.pdf lightcommands.pdf trafficlightctrl.pdf

scy: trafficlightctrl.scy

trafficlightctrl.scy: trafficlightctrl.yml timer.scy control.scy policeinterrupt.scy lightcommands.scy

crossroad_controller.scy: crossroad_controller.yml trafficlightctrl.scy timer.scy control.scy policeinterrupt.scy

clean:
	rm -f *.scy *.pdf *.int

.PHONY: all pdf scy
