SHELLEYC = shelleyc
SHELLEYVIZ = shelleyv

all: scy pdf

pdf: singleclick.pdf smartbutton.pdf

scy: smartbutton.scy

smartbutton.scy: smartbutton.yml singleclick.scy
	$(SHELLEYC) -d $< -u singleclick.scy\:SingleClickButton

%.scy: %.yml
	$(SHELLEYC) -d $<

%.gv: %.scy
	$(SHELLEYVIZ) $< -o $@

%.pdf: %.gv
	dot -Tpdf -o $@ $<

clean:
	rm -f *.scy *.pdf *.gv