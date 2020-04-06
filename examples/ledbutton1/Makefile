PYTHON = PYTHONPATH=../../ python3
SHELLYC = $(PYTHON) -m appcompiler
SHELLYVIZ = $(PYTHON) -m appvizviewer

all: ledbutton_led ledbutton_ledstrict ledbuttonstrict_ledstrict viz

%.scy: %.yaml
	$(SHELLYC) -d $<

ledbutton_led: ledbutton.yaml led.scy button.scy
	$(SHELLYC) -d $< -u button.scy\:Button led.scy\:Led

ledbutton_ledstrict: ledbutton_ledstrict.yaml led_strict.scy button.scy
	# This should fail: led is now more strict and we must observe (on off)*
	! $(SHELLYC) -d $< -u button.scy\:Button led_strict.scy\:LedStrict

ledbuttonstrict_ledstrict: ledbuttonstrict_ledstrict.yaml led_strict.scy button.scy
	# This is ok: led is more strict but ledbutton is also more strict
	$(SHELLYC) -d $< -u button.scy\:Button led_strict.scy\:LedStrict

viz:
	$(SHELLYVIZ) -i button.scy
	$(SHELLYVIZ) -i led.scy
	$(SHELLYVIZ) -i led_strict.scy
	$(SHELLYVIZ) -i ledbutton.scy
	# $(SHELLYVIZ) -i ledbutton_ledstrict.scy
	$(SHELLYVIZ) -i ledbuttonstrict_ledstrict.scy

clean:
	rm -f *.scy
	rm -f *.gv
	rm -f *.pdf

.SUFFIXES: .yaml .scy
