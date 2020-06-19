include ../common.mk
.PHONY: all pdf scy clean all

all: scy

pdf: button.pdf smartbutton.pdf

scy: smartbutton.scy

USES = -u uses.yml

smartbutton.scy: smartbutton.yml button.scy

clean:
	rm -f *.scy *.pdf *.gv