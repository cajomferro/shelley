PYTHON = PYTHONPATH=../../ python3
SHELLYC = $(PYTHON) -m appcompiler

all: sendok.scy

%.scy: %.yaml
	$(SHELLYC) -d $<

sendok.scy: sendok.yaml led.scy button.scy
	$(SHELLYC) -d $< -u button.scy\:Button led.scy\:Led

clean:
	rm -f *.scy

.SUFFIXES: .yaml .scy
