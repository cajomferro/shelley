PYTHON = PYTHONPATH=../../../ python3
SHELLYC = $(PYTHON) -m shelleyc
SHELLYVIZ = $(PYTHON) -m shelleyv

all: scy pdf

pdf: simple_button.pdf led.pdf ledbutton.pdf

scy: ledbutton.scy

ledbutton.scy: ledbutton.yml simple_button.scy led.scy
	# This is ok: led is more strict but ledbutton is also more strict
	$(SHELLYC) -d $< -u simple_button.scy\:SimpleButton led.scy\:Led

%.scy: %.yml
	$(SHELLYC) -d $<

%.gv: %.scy
	$(SHELLYVIZ) $< -o $@

%.pdf: %.gv
	dot -Tpdf -o $@ $<

clean:
	rm -f *.scy *.pdf *.gv

.SUFFIXES: .yml .scy
