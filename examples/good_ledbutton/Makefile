include ../common.mk
.PHONY: all pdf scy clean all

all: scy

pdf: simple_button.pdf led.pdf ledbutton.pdf

scy: ledbutton.scy

USES = -u uses.yml
# This is ok: led is more strict but ledbutton is also more strict
ledbutton.scy: ledbutton.yml ../base/simple_button.scy led.scy

clean:
	rm -f *.scy *.pdf *.gv
