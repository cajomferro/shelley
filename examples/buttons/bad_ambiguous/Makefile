PYTHON = PYTHONPATH=../../../ python3
SHELLYC = $(PYTHON) -m shelleyc
SHELLYVIZ = $(PYTHON) -m shelleyv

all: scy pdf

pdf: simple.pdf

scy: ambiguous.scy

ambiguous.scy: ambiguous.yml simple.scy
	# Invalid device: AmbiguousTriggersFailure
	! $(SHELLYC) -d $< -u simple.scy\:SimpleButton

%.scy: %.yml
	$(SHELLYC) -d $<

%.gv: %.scy
	$(SHELLYVIZ) $< -o $@

%.pdf: %.gv
	dot -Tpdf -o $@ $<

clean:
	rm -f *.scy *.pdf *.gv