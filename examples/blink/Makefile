include ../common.mk
.PHONY: all pdf scy clean all

all: scy

pdf: led.pdf timer.pdf

scy: blink.scy

blink.scy: blink.yml ../base/timer.scy ../base/led.scy

clean:
	rm -f *.scy *.pdf *.png *.int
