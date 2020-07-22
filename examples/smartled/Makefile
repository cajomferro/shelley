include ../common.mk
.PHONY: all pdf scy clean all

all: scy

pdf: led.pdf timer.pdf 

scy: smartled.scy

smartled.scy: smartled.yml ../base/timer.scy ../base/led.scy

clean:	
	rm -f *.scy *.pdf *.gv
