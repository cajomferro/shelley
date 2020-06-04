include ../common.mk

all: scy

pdf: magnetic.pdf radio.pdf valve.pdf lowpower-strict.pdf controller.pdf

scy: controller.scy

controller.scy: controller.yml valve.scy magnetic.scy radio.scy lowpower-strict.scy

clean:
	rm -f *.scy *.pdf *.gv
