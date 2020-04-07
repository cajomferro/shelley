PYTHON = PYTHONPATH=../../ python3
SHELLYC = $(PYTHON) -m appcompiler
SHELLYVIZ = $(PYTHON) -m appvizviewer

all: scy pdf

pdf: button.pdf led.pdf timer.pdf desklamp.pdf

scy: desklamp.scy

desklamp.scy: desklamp.yaml timer.scy led.scy button.scy
	$(SHELLYC) -d $< -u button.scy\:Button led.scy\:Led timer.scy\:Timer

%.scy: %.yaml
	$(SHELLYC) -d $<

%.gv: %.scy
	$(SHELLYVIZ) $< -o $@

%.pdf: %.gv
	dot -Tpdf -o $@ $<

clean:
	rm -f *.scy *.pdf *.gv


.SUFFIXES: .yaml .scy
