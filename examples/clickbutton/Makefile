include ../common.mk
.PHONY: all pdf scy clean all

all: scy

pdf: button.pdf timer.pdf clickbutton.pdf

scy: clickbutton.scy

clickbutton.scy: clickbutton.yml timer.scy button.scy

clean:
	rm -f *.scy *.pdf *.int
