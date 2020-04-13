PYTHON = PYTHONPATH=../../../ python3
SHELLYC = $(PYTHON) -m appcompiler
SHELLYVIZ = $(PYTHON) -m appvizviewer

all: scy pdf

pdf: singleclick.pdf timer.pdf smartbutton.pdf

scy: smartbutton.scy

smartbutton.scy: smartbutton.yml singleclick.scy timer.scy
	$(SHELLYC) -d $< -u singleclick.scy\:SingleClickButton timer.scy\:Timer

%.scy: %.yml
	$(SHELLYC) -d $<

%.gv: %.scy
	$(SHELLYVIZ) $< -o $@

%.pdf: %.gv
	dot -Tpdf -o $@ $<

clean:
	rm -f *.scy *.pdf *.gv