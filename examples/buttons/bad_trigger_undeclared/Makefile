PYTHON = PYTHONPATH=../../../ python3
SHELLYC = $(PYTHON) -m appcompiler
SHELLYVIZ = $(PYTHON) -m appvizviewer

all: scy pdf

pdf: singleclick.pdf

scy: trigger_undeclared.scy

trigger_undeclared.scy: trigger_undeclared.yml singleclick.scy
	# Shelley parser error: Trigger event 'off' has not been declared
	! $(SHELLYC) -d $< -u singleclick.scy\:SingleClickButton

%.scy: %.yml
	$(SHELLYC) -d $<

%.gv: %.scy
	$(SHELLYVIZ) $< -o $@

%.pdf: %.gv
	dot -Tpdf -o $@ $<

clean:
	rm -f *.scy *.pdf *.gv