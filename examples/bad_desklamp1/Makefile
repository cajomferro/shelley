include ../common.mk
.PHONY: all pdf scy clean all

all: scy

pdf: button.pdf led.pdf timer.pdf desklamp.pdf

scy: desklamp.scy

desklamp.scy: desklamp.yml ../base/timer.scy ../base/led.scy ../base/button.scy
	# Negate the result, since this should fail
	@$(SHELLEYC) $(USES) -d $< -o $@ --skip-checks
	! $(SHELLEYC) $(USES) -d $< --no-output

clean:
	rm -f *.scy *.pdf
