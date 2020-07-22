include ../common.mk
.PHONY: all pdf scy clean all

all: scy

pdf: ../base/led.pdf ../base/timer.pdf 

scy: smartled2.scy

smartled2.scy: smartled2.yml ../base/timer.scy ../base/led.scy

clean:	
	rm -f *.scy *.pdf *.gv
