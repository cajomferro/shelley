PYTHON = PYTHONPATH=../../../ python3
SHELLYVIZ = $(PYTHON) -m appvizviewer

all: possible nfa dfa

possible: dev-all-possible-dfa.pdf dev-all-possible-dfa-minimized-notraps.pdf dev-all-possible-dfa-minimized-traps.pdf

nfa:  dev-micro-nfa-no-epsilon-no-traps.pdf dev-micro-nfa.pdf dev-micro-nfa-no-epsilon.pdf dev-micro-nfa-no-traps.pdf

dfa: dev-micro-dfa.pdf dev-micro-dfa-minimized.pdf dev-micro-dfa-minimized-no-traps.pdf

%.gv: %.scy
	$(SHELLYVIZ) $< -o $@

%.pdf: %.gv
	dot -Tpdf -o $@ $<

clean:
	rm -f *.pdf *.gv

clean-scy:
	rm -f *.scy

clean-all: clean clean-scy