SHELLEYC = shelleyc
SHELLEYV = shelleyv

all: scy

pdf: button.pdf smartbutton.pdf

scy: smartbutton.scy

smartbutton.scy: smartbutton.yml button.scy
	$(SHELLEYC) -d $< -u button.scy\:Button

%.scy: %.yml
	$(SHELLEYC) -d $<

%.gv: %.scy
	$(SHELLEYV) $< -o $@

%.pdf: %.gv
	dot -Tpdf -o $@ $<

clean:
	rm -f *.scy *.pdf *.gv