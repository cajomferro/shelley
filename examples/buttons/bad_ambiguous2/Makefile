PYTHON = PYTHONPATH=../../../ python3
SHELLYC = $(PYTHON) -m shelleyc
SHELLYVIZ = $(PYTHON) -m shelleyv

all: scy pdf

pdf: singleclick.pdf timer.pdf

scy: ambiguous.scy

ambiguous.scy: ambiguous.yml singleclick.scy timer.scy
	# Invalid device: AmbiguousTriggersFailure
	! $(SHELLYC) -d $< -u singleclick.scy\:SingleClickButton timer.scy\:Timer

%.scy: %.yml
	$(SHELLYC) -d $<

%.gv: %.scy
	$(SHELLYVIZ) $< -o $@

%.pdf: %.gv
	dot -Tpdf -o $@ $<

clean:
	rm -f *.scy *.pdf *.gv