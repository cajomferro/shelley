include ../common.mk
.PHONY: all pdf scy clean all

all: scy

pdf: button.pdf smartbutton.pdf

scy: smartbutton.scy

smartbutton.scy: smartbutton.yml ../base/pressed_button.scy

clean:
	rm -f *.scy *.pdf *.gv