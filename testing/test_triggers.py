import unittest
from events import EEvent
from triggers.checker import check, TriggersEventUndeclaredError, TriggersListDuplicatedError, TriggersListEmptyError, \
    TriggerRuleDeviceNotDeclaredError, TriggerRuleEventNotDeclaredError
from testing.creator import create_device_led, create_device_button, create_device_timer, create_device_desk_lamp
from triggers import Trigger, TriggerRule, TriggerRuleSequence, TriggerRuleEvent
from devices import get_devices_from_trigger_rule


class TestTriggers(unittest.TestCase):
    def test_is_valid(self):
        d_led_a = create_device_led()
        d_button = create_device_button()
        d_timer = create_device_timer()

        e_level1 = EEvent('level1')
        e_standby1 = EEvent('standby1')
        events = [e_level1, e_standby1]

        components = {
            "ledA": d_led_a,
            "b": d_button,
            "t": d_timer,
        }

        t_level1_trules = TriggerRuleSequence(TriggerRuleEvent("b", "pressed"),
                                              TriggerRuleSequence(TriggerRuleEvent("b", "released"),
                                                                  TriggerRuleSequence(TriggerRuleEvent("ledA", "on"),
                                                                                      TriggerRuleEvent("t",
                                                                                                       "started"))))

        t_level1 = Trigger(e_level1, t_level1_trules)

        t_standby1_trules = TriggerRuleSequence(TriggerRuleEvent("t", "timeout"), TriggerRuleEvent("ledA", "off"))
        t_standby1 = Trigger(e_standby1, t_standby1_trules)

        triggers = [t_level1, t_standby1]

        original_triggers_len = len(triggers)

        result = []  # type: List[Trigger]
        check(triggers, events, components, result)

        self.assertEqual(get_devices_from_trigger_rule(t_level1_trules), {'b', 't', 'ledA'})
        self.assertEqual(get_devices_from_trigger_rule(t_standby1_trules), {'t', 'ledA'})

        self.assertEqual(original_triggers_len, len(result))

    def test_undeclared_component(self):
        d_led_a = create_device_led()
        d_button = create_device_button()
        d_timer = create_device_timer()

        e_level1 = EEvent('level1')
        e_standby1 = EEvent('standby1')
        events = [e_level1, e_standby1]

        components = {
            # "ledA": d_led_a, TEST HERE
            "b": d_button,
            "t": d_timer,
        }

        t_level1_trules = TriggerRuleSequence(TriggerRuleEvent("b", "pressed"),
                                              TriggerRuleSequence(TriggerRuleEvent("b", "released"),
                                                                  TriggerRuleSequence(TriggerRuleEvent("ledA", "on"),
                                                                                      TriggerRuleEvent("t",
                                                                                                       "started"))))
        t_level1 = Trigger(e_level1, t_level1_trules)

        t_standby1_trules = TriggerRuleSequence(TriggerRuleEvent("t", "timeout"), TriggerRuleEvent("ledA", "off"))
        t_standby1 = Trigger(e_standby1, t_standby1_trules)

        triggers = [t_level1, t_standby1]

        with self.assertRaises(TriggerRuleDeviceNotDeclaredError) as context:
            check(triggers, events, components, [])

    def test_undeclared_event(self):
        d_led_a = create_device_led()
        d_button = create_device_button()
        d_timer = create_device_timer()

        e_level1 = EEvent('level1')
        e_standby1 = EEvent('standby1')
        events = [e_level1, e_standby1]

        components = {
            "ledA": d_led_a,
            "b": d_button,
            "t": d_timer,
        }

        t_level1_trules = TriggerRuleSequence(TriggerRuleEvent("b", "undeclared_event"),  # TEST HERE
                                              TriggerRuleSequence(TriggerRuleEvent("b", "released"),
                                                                  TriggerRuleSequence(TriggerRuleEvent("ledA", "on"),
                                                                                      TriggerRuleEvent("t",
                                                                                                       "started"))))
        t_level1 = Trigger(e_level1, t_level1_trules)

        t_standby1_trules = TriggerRuleSequence(TriggerRuleEvent("t", "timeout"), TriggerRuleEvent("ledA", "off"))
        t_standby1 = Trigger(e_standby1, t_standby1_trules)

        triggers = [t_level1, t_standby1]

        with self.assertRaises(TriggerRuleEventNotDeclaredError) as context:
            check(triggers, events, components, [])

    def test_undeclared_event_2(self):
        d_led_a = create_device_led()
        d_button = create_device_button()
        d_timer = create_device_timer()

        e_level1 = EEvent('level1')
        e_standby1 = EEvent('standby1')
        events = [e_level1, e_standby1]

        components = {
            "ledA": d_led_a,
            "b": d_button,
            "t": d_timer,
        }

        t_level1_trules = TriggerRuleSequence(TriggerRuleEvent("b", "pressed"),
                                              TriggerRuleSequence(TriggerRuleEvent("b", "released"),
                                                                  TriggerRuleSequence(TriggerRuleEvent("ledA", "on"),
                                                                                      TriggerRuleEvent("t",
                                                                                                       "undeclared event"))))  # TEST HERE
        t_level1 = Trigger(e_level1, t_level1_trules)

        t_standby1_trules = TriggerRuleSequence(TriggerRuleEvent("t", "timeout"), TriggerRuleEvent("ledA", "off"))
        t_standby1 = Trigger(e_standby1, t_standby1_trules)

        triggers = [t_level1, t_standby1]

        with self.assertRaises(TriggerRuleEventNotDeclaredError) as context:
            check(triggers, events, components, [])

    def test_duplicated(self):
        d_led_a = create_device_led()

        components = {
            "ledA": d_led_a
        }

        e_level1 = EEvent('level1')
        e_standby1 = EEvent('standby1')

        declared_e_events = [e_level1, e_standby1]

        t_level1 = Trigger(e_level1, TriggerRuleEvent("ledA", "on"))  # random rules here, doesn't matter

        t_standby1 = Trigger(e_standby1, TriggerRuleEvent("ledA", "on"))  # random rules here, doesn't matter

        triggers = [t_level1, t_standby1, t_level1]

        result = []  # type: List[Trigger]

        with self.assertRaises(TriggersListDuplicatedError) as context:
            check(triggers, declared_e_events, components, result)

    def test_empty(self):
        with self.assertRaises(TriggersListEmptyError) as context:
            check([], [], {}, [])

    def test_event_not_declared(self):
        e_level1 = EEvent('level1')
        e_standby1 = EEvent('standby1')

        declared_e_events = [e_level1]

        t_level1 = Trigger(e_level1, None)

        t_standby1 = Trigger(e_standby1, None)

        triggers = [t_level1, t_standby1]

        result = []  # type: List[Trigger]

        with self.assertRaises(TriggersEventUndeclaredError) as context:
            check(triggers, declared_e_events, {}, result)


if __name__ == '__main__':
    unittest.main()
