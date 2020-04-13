all:
	$(MAKE) -C desklamp/bad_desklamp1
	$(MAKE) -C desklamp/good_desklamp
	$(MAKE) -C sendok
	$(MAKE) -C buttons/bad_ambiguous
	$(MAKE) -C buttons/bad_ambiguous2
	$(MAKE) -C buttons/bad_missing_trigger
	$(MAKE) -C buttons/bad_smartbutton
	$(MAKE) -C buttons/bad_trigger_undeclared
	$(MAKE) -C buttons/good_smartbutton
	$(MAKE) -C buttons/good_smartbutton2

clean:
	$(MAKE) -C desklamp/bad_desklamp1 clean
	$(MAKE) -C desklamp/good_desklamp clean
	$(MAKE) -C sendok clean
	$(MAKE) -C buttons/bad_ambiguous clean
	$(MAKE) -C buttons/bad_ambiguous2 clean
	$(MAKE) -C buttons/bad_missing_trigger clean
	$(MAKE) -C buttons/bad_smartbutton clean
	$(MAKE) -C buttons/bad_trigger_undeclared clean
	$(MAKE) -C buttons/good_smartbutton clean
	$(MAKE) -C buttons/good_smartbutton2 clean