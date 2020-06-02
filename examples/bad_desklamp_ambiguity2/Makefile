SHELLEYC = shelleyc
SHELLEYV = shelleyv

all: scy

pdf: button.pdf led.pdf timer.pdf desklamp.pdf

scy: desklamp.scy

desklamp.scy: desklamp.yml timer.scy led.scy button.scy
	# Negate the result, since this should fail
	! $(SHELLEYC) -d $< -u uses.yml -o $@ # -v

%.scy: %.yml
	$(SHELLEYC) -d $< -o $@

%.pdf: %.scy
	$(SHELLEYV) --format pdf $< -o $@

clean:
	rm -f *.scy *.pdf

.PHONY: all pdf scy

.SUFFIXES: .yml .scy
