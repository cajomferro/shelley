include ../common.mk
.PHONY: all pdf scy clean all

all: scy

pdf: button.pdf led.pdf timer.pdf desklamp.pdf

scy: desklamp.scy

desklamp.scy: desklamp.yml timer.scy led.scy button.scy
	# Negate the result, since this should fail
	! $(SHELLEYC) -d $< -u uses.yml -o $@ # -v

clean:
	rm -f *.scy *.pdf
