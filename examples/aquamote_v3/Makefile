SHELLEYC = shelleyc
SHELLEYV = shelleyv

all: scy

pdf: magnetic.pdf httpclient.pdf wificlient.pdf radio.pdf valve.pdf timer.pdf valvehandlertimer.pdf lowpower-strict.pdf controller.pdf # micro-pdf

# run with make internal SHELLEYC="shelleyc -i"
internal: pdf controller-micro-dfa-minimized.pdf controller-micro-dfa-minimized-no-traps.pdf controller-micro-nfa-no-epsilon-no-traps.pdf # controller-shuffle-dfa-minimized.pdf controller-shuffle-dfa-minimized-no-traps.pdf

internal-radio: radio-micro-dfa-minimized.pdf radio-micro-dfa-minimized-no-traps.pdf radio-micro-nfa-no-epsilon-no-traps.pdf

scy: controller.scy radio.scy valvehandlertimer.scy

radio.scy: radio.yml wificlient.scy httpclient.scy

valvehandlertimer.scy: valvehandlertimer.yml valve.scy timer.scy

controller.scy: controller.yml valvehandlertimer.scy magnetic.scy radio.scy lowpower-strict.scy

#controller-%.scy:
#	$(SHELLEYC) -u uses.yml -d $< -o $@

%.scy: %.yml
	$(SHELLEYC) -u uses.yml -d $< -o $@

%.gv: %.scy
	$(SHELLEYV) $< -o $@

%.pdf: %.gv
	dot -Tpdf -o $@ $<

clean:
	rm -f *.scy *.pdf *.gv


.SUFFIXES: .yml .scy
