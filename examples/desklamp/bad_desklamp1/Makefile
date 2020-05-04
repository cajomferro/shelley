SHELLEYC = shelleyc
SHELLEYVIZ = shelleyv

all: desklamp.scy

%.scy: %.yml
	$(SHELLEYC) -d $<

desklamp.scy: desklamp.yml timer.scy led.scy button.scy
	# Negate the result, since this should fail
	! $(SHELLEYC) -d $< -u button.scy\:Button led.scy\:Led timer.scy\:Timer

clean:
	rm -f *.scy

.SUFFIXES: .yml .scy
