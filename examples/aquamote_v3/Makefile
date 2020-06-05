include ../common.mk

all: scy

pdf: magnetic.pdf httpclient.pdf wificlient.pdf radio.pdf valve.pdf timer.pdf valvehandlertimer.pdf lowpower-strict.pdf controller.pdf

scy: controller.scy radio.scy valvehandlertimer.scy

radio.scy: radio.yml wificlient.scy httpclient.scy

valvehandlertimer.scy: valvehandlertimer.yml valve.scy timer.scy

controller.scy: controller.yml valvehandlertimer.scy magnetic.scy radio.scy lowpower-strict.scy

clean:
	rm -f *.scy *.pdf *.int

.PHONY: all pdf scy
