SHELLEYC = shelleyc
SHELLEYV = shelleyv

all: scy

scy: desklamp.scy

desklamp.scy: desklamp.yml timer.scy led.scy button.scy
	@$(SHELLEYC) -u uses.yml -d $< -o $@ --skip-checks
	! $(SHELLEYC) -u uses.yml -d $< --no-output

%.scy: %.yml
	$(SHELLEYC) -u uses.yml -d $< -o $@

clean:
	rm -f *.scy *.pdf

.PHONY: all pdf scy

.SUFFIXES: .yml .scy
