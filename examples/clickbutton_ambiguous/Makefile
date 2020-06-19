include ../common.mk
.PHONY: all pdf scy clean all

all: scy

pdf: button.pdf timer.pdf clickbutton.pdf

scy: clickbutton.scy

clickbutton.scy: clickbutton.yml ../base/timer.scy ../base/button.scy
	@$(SHELLEYC) $(USES) -d $< -o $@ --skip-checks
	! $(SHELLEYC) $(USES) -d $< --no-output

clean:
	rm -f *.scy *.pdf *.int
