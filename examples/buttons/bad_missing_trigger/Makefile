PYTHON = PYTHONPATH=../../../ python3
SHELLYC = $(PYTHON) -m appcompiler
SHELLYVIZ = $(PYTHON) -m appvizviewer

all: scy pdf

pdf: singleclick.pdf

scy: missing_trigger.scy

missing_trigger.scy: missing_trigger.yml singleclick.scy
	# Shelley parser error: Missing trigger for event 'off'
	! $(SHELLYC) -d $< -u singleclick.scy\:SingleClickButton

%.scy: %.yml
	$(SHELLYC) -d $<

%.gv: %.scy
	$(SHELLYVIZ) $< -o $@

%.pdf: %.gv
	dot -Tpdf -o $@ $<

clean:
	rm -f *.scy *.pdf *.gv