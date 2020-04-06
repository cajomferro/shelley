PYTHON = PYTHONPATH=../../ python3
SHELLYC = $(PYTHON) -m appcompiler
SHELLYVIZ = $(PYTHON) -m appvizviewer
OUTDIR = compiled
EXTENSIONS=scy scb pdf png svg jpg jpeg tif tiff eps dot json ps gv

all: ledbutton_led ledbutton_ledstrict ledbuttonstrict_ledstrict

%.scy: %.yaml
	$(SHELLYC) -d $< -o $(OUTDIR)

ledbutton_led: ledbutton.yaml led.scy button.scy
	$(SHELLYC) -d $< -u $(OUTDIR)/button.scy\:Button $(OUTDIR)/led.scy\:Led -o $(OUTDIR)

ledbutton_ledstrict: ledbutton_ledstrict.yaml led_strict.scy button.scy
	# This should fail: led is now more strict and we must observe (on off)*
	! $(SHELLYC) -d $< -u $(OUTDIR)/button.scy\:Button $(OUTDIR)/led_strict.scy\:LedStrict -o $(OUTDIR)

ledbuttonstrict_ledstrict: ledbuttonstrict_ledstrict.yaml led_strict.scy button.scy
	# This is ok: led is more strict but ledbutton is also more strict
	$(SHELLYC) -d $< -u $(OUTDIR)/button.scy\:Button $(OUTDIR)/led_strict.scy\:LedStrict -o $(OUTDIR)

viz:
	$(SHELLYVIZ) -i $(OUTDIR)/button.scy
	$(SHELLYVIZ) -i $(OUTDIR)/led.scy
	$(SHELLYVIZ) -i $(OUTDIR)/led_strict.scy
	$(SHELLYVIZ) -i $(OUTDIR)/ledbutton.scy
	# $(SHELLYVIZ) -i $(OUTDIR)/ledbutton_ledstrict.scy
	$(SHELLYVIZ) -i $(OUTDIR)/ledbuttonstrict_ledstrict.scy

clean:
	rm -rf $(foreach postfix, $(EXTENSIONS), $(OUTDIR)/*.$(postfix))

.SUFFIXES: .yaml .scy
