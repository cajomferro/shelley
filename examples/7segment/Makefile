include ../common.mk
.PHONY: all pdf scy clean all

all: scy

pdf: led.pdf

scy: 7segment.scy ../base/led.scy

#7segment.scy: 7segment.yml ../base/led.scy

clean:	
	rm -f *.scy *.pdf *.gv
