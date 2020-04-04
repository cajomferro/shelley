PYTHON = PYTHONPATH=../../ python3
SHELLYC = $(PYTHON) -m appcompiler

all: desklamp.scy

%.scy: %.yaml
	$(SHELLYC) -d $<

desklamp.scy: desklamp.yaml timer.scy led.scy button.scy
	$(SHELLYC) -d $< -u button.scy\:Button led.scy\:Led timer.scy\:Timer

clean:
	rm -f *.scy

.SUFFIXES: .yaml .scy
