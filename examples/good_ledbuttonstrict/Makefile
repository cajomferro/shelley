include ../common.mk
.PHONY: all pdf scy clean all

all: scy

pdf: simple_button.pdf led_strict.pdf ledbutton.pdf

scy: ledbutton.scy

# This is ok: led is more strict but ledbutton is also more strict
ledbutton.scy: ledbutton.yml ../base/simple_button.scy ../base/led_strict.scy

clean:
	rm -f *.scy *.pdf *.gv
