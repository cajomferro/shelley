PYTHON = PYTHONPATH=../../ python3
SHELLYC = $(PYTHON) -m appcompiler

all: smartbutton.scy

%.scy: %.yaml
	$(SHELLYC) -d $<

smartbutton.scy: smartbutton.yaml button.scy
	$(SHELLYC) -d $< -u button.scy\:Button

clean:
	rm -f *.scy

.SUFFIXES: .yaml .scy
