all:
	$(MAKE) -C desklamp/bad_desklamp1
	$(MAKE) -C desklamp/good_desklamp
	$(MAKE) -C desklamp/good_simple_desklamp
	$(MAKE) -C desklamp/good_simple_desklamp2
	$(MAKE) -C sendok/good_sendok
	$(MAKE) -C buttons/bad_ambiguous
	$(MAKE) -C buttons/bad_ambiguous2
	$(MAKE) -C buttons/bad_missing_trigger
	$(MAKE) -C buttons/bad_smartbutton
	$(MAKE) -C buttons/bad_trigger_undeclared
	$(MAKE) -C buttons/good_smartbutton
	$(MAKE) -C buttons/good_smartbutton2
	$(MAKE) -C buttons/good_ledbutton
	$(MAKE) -C buttons/good_ledbuttonstrict
	$(MAKE) -C buttons/bad_ledbuttonstrict

	$(MAKE) -C watering/v1
	$(MAKE) -C watering/v2
	$(MAKE) -C watering/v2_finalstates
	$(MAKE) -C watering/v2_valve
	$(MAKE) -C watering/v2_valvehandler
	$(MAKE) -C watering/v2_valvehandlertimer
	$(MAKE) -C watering/v3

clean:
	$(MAKE) -C desklamp/bad_desklamp1 clean
	$(MAKE) -C desklamp/good_desklamp clean
	$(MAKE) -C desklamp/good_simple_desklamp clean
	$(MAKE) -C desklamp/good_simple_desklamp2 clean
	$(MAKE) -C sendok/good_sendok clean
	$(MAKE) -C buttons/bad_ambiguous clean
	$(MAKE) -C buttons/bad_ambiguous2 clean
	$(MAKE) -C buttons/bad_missing_trigger clean
	$(MAKE) -C buttons/bad_smartbutton clean
	$(MAKE) -C buttons/bad_trigger_undeclared clean
	$(MAKE) -C buttons/good_smartbutton clean
	$(MAKE) -C buttons/good_smartbutton2 clean
	$(MAKE) -C buttons/good_ledbutton clean
	$(MAKE) -C buttons/good_ledbuttonstrict clean
	$(MAKE) -C buttons/bad_ledbuttonstrict clean

	$(MAKE) -C watering/v1 clean
	$(MAKE) -C watering/v2 clean
	$(MAKE) -C watering/v2_finalstates clean
	$(MAKE) -C watering/v2_valve clean
	$(MAKE) -C watering/v2_valvehandler clean
	$(MAKE) -C watering/v2_valvehandlertimer clean
	$(MAKE) -C watering/v3 clean

watering-timer:
	time $(MAKE) -C watering/v1 scy
	time $(MAKE) -C watering/v2 scy
	time $(MAKE) -C watering/v2_finalstates scy
	time $(MAKE) -C watering/v2_valve scy
	time $(MAKE) -C watering/v2_valvehandler scy
	time $(MAKE) -C watering/v2_valvehandlertimer scy
	time $(MAKE) -C watering/v3 scy