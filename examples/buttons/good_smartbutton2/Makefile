SHELLEYC = shelleyc
SHELLEYVIZ = shelleyv

all: scy pdf

pdf: singleclick.pdf timer.pdf smartbutton.pdf

scy: smartbutton.scy

smartbutton.scy: smartbutton.yml singleclick.scy timer.scy
	$(SHELLEYC) -d $< -u singleclick.scy\:SingleClickButton timer.scy\:Timer

%.scy: %.yml
	$(SHELLEYC) -d $<

%.gv: %.scy
	$(SHELLEYVIZ) $< -o $@

%.pdf: %.gv
	dot -Tpdf -o $@ $<

clean:
	rm -f *.scy *.pdf *.gv