PYTHON = PYTHONPATH=../../../ python3
SHELLYC = $(PYTHON) -m appcompiler
SHELLYVIZ = $(PYTHON) -m appvizviewer

all: scy pdf

pdf: button.pdf led.pdf sendok.pdf

scy: sendok.scy

sendok.scy: sendok.yml led.scy button.scy
	$(SHELLYC) -d $< -u button.scy\:Button led.scy\:Led

%.scy: %.yml
	$(SHELLYC) -d $< -o $@
	test -f $<

%.gv: %.scy
	$(SHELLYVIZ) $< -o $@

%.pdf: %.gv
	dot -Tpdf -o $@ $<

clean:
	rm -f *.scy *.pdf *.gv


.SUFFIXES: .yml .scy