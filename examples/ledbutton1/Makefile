PYTHON = PYTHONPATH=../../ python3
SHELLYC = $(PYTHON) -m appcompiler
SHELLYVIZ = $(PYTHON) -m appvizviewer

all: ledbutton_led ledbutton_ledstrict ledbuttonstrict_ledstrict pdf

pdf: button.pdf led.pdf led_strict.pdf ledbutton.pdf ledbuttonstrict_ledstrict.pdf

ledbutton_led: ledbutton.yaml led.scy button.scy
	$(SHELLYC) -d $< -u button.scy\:Button led.scy\:Led

ledbutton_ledstrict: ledbutton_ledstrict.yaml led_strict.scy button.scy
	# This should fail: led is now more strict and we must observe (on off)*
	! $(SHELLYC) -d $< -u button.scy\:Button led_strict.scy\:LedStrict

ledbuttonstrict_ledstrict: ledbuttonstrict_ledstrict.yaml led_strict.scy button.scy
	# This is ok: led is more strict but ledbutton is also more strict
	$(SHELLYC) -d $< -u button.scy\:Button led_strict.scy\:LedStrict

%.scy: %.yaml
	$(SHELLYC) -d $<

%.gv: %.scy
	$(SHELLYVIZ) $< -o $@

%.pdf: %.gv
	dot -Tpdf -o $@ $<

clean:
	rm -f *.scy *.pdf *.gv

.SUFFIXES: .yaml .scy
