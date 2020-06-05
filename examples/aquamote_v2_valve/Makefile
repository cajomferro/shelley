include ../common.mk

all: scy

pdf: magnetic.pdf radio.pdf radiosimple.pdf radiosimplest.pdf valve.pdf lowpower-strict.pdf controller.pdf

scy: controller.scy radiosimple.scy

radiosimple.scy: radiosimple.yml radio.scy

radiosimplest.scy: radiosimplest.yml radiosimple.scy

controller.scy: controller.yml valve.scy magnetic.scy radiosimplest.scy lowpower-strict.scy

clean:
	rm -f *.scy *.pdf *.gv

.PHONY: all pdf scy
