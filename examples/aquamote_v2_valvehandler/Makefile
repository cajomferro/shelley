include ../common.mk

all: scy

pdf: magnetic.pdf radio.pdf radiosimple.pdf radiosimplest.pdf valve.pdf valvehandler.pdf lowpower-strict.pdf controller.pdf

scy: controller.scy radiosimple.scy valvehandler.scy

radiosimple.scy: radiosimple.yml radio.scy

radiosimplest.scy: radiosimplest.yml radiosimple.scy

valvehandler.scy: valvehandler.yml valve.scy

controller.scy: controller.yml valvehandler.scy magnetic.scy radiosimplest.scy lowpower-strict.scy

clean:
	rm -f *.scy *.pdf *.gv

.PHONY: all pdf scy
