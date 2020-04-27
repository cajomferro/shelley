PYTHON = PYTHONPATH=../../../ python3
SHELLYC = $(PYTHON) -m shelleyc
SHELLYVIZ = $(PYTHON) -m shelleyv

all: scy pdf

pdf: singleclick.pdf smartbutton.pdf

scy: smartbutton.scy

smartbutton.scy: smartbutton.yml singleclick.scy
	$(SHELLYC) -d $< -u singleclick.scy\:SingleClickButton

%.scy: %.yml
	$(SHELLYC) -d $<

%.gv: %.scy
	$(SHELLYVIZ) $< -o $@

%.pdf: %.gv
	dot -Tpdf -o $@ $<

clean:
	rm -f *.scy *.pdf *.gv