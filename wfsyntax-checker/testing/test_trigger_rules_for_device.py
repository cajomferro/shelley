import unittest

from typing import List, Tuple

from _local.devices import Device
from triggers import Trigger
from testing.creator import create_device_led, create_device_button, create_device_timer, create_device_desk_lamp
from events.checker import check as check_events
from behaviours.checker import check as check_behaviours
from components.checker import check as check_components
from triggers.checker import check as check_triggers
from events import GenericEvent, EEvent, IEvent
from triggers import TriggerRuleSequence, TriggerRuleEvent, TriggerRuleChoice
from _local.devices import get_rules_by_device


class TestGetDevicesAsSet(unittest.TestCase):

    def setUp(self):
        d_led_a = create_device_led()
        d_led_b = create_device_led()
        d_button = create_device_button()
        d_timer = create_device_timer()
        d_desk_lamp = create_device_desk_lamp(d_led_a, d_led_b, d_button, d_timer)

        declared_devices = {
            d_led_a.name: d_led_a,
            d_led_b.name: d_led_b,
            d_button.name: d_button,
            d_timer.name: d_timer,
        }

        declared_i_events, declared_e_events = check_events(
            d_desk_lamp.get_all_events())  # type: List[IEvent], List[EEvent]

        behaviours_result = []  # type: List[Tuple[GenericEvent, GenericEvent]]
        check_behaviours(d_desk_lamp.behaviours, d_desk_lamp.actions, declared_i_events, declared_e_events,
                         behaviours_result)

        declared_components = check_components(d_desk_lamp.components, d_desk_lamp.uses,
                                               declared_devices)  # type: Dict[str, Device]

        self.triggers_result = []  # type: List[Trigger]
        check_triggers(d_desk_lamp.triggers, declared_e_events, declared_components, self.triggers_result)

        self.declared_components = declared_components

    def test_sequence(self):
        expected_trace = TriggerRuleEvent("b", "released")

        self.assertEqual(expected_trace, get_rules_by_device("b", TriggerRuleSequence(
            TriggerRuleEvent("b", "released"),
            TriggerRuleEvent("t", "canceled"))))

        expected_trace = TriggerRuleEvent("t", "canceled")

        self.assertEqual(expected_trace, get_rules_by_device("t", TriggerRuleSequence(
            TriggerRuleEvent("b", "released"),
            TriggerRuleEvent("t", "canceled"))))

    def test_sequence_3_elems(self):
        expected_trace = TriggerRuleEvent("b", "released")

        self.assertEqual(expected_trace, get_rules_by_device("b", TriggerRuleSequence(
            TriggerRuleEvent("b", "released"),
            TriggerRuleSequence(
                TriggerRuleEvent("t", "canceled"),
                TriggerRuleEvent("ledA", "on")))))

    def test_sequence_4_elems(self):
        expected_trace = TriggerRuleEvent("b", "released")

        self.assertEqual(expected_trace, get_rules_by_device("b", TriggerRuleSequence(
            TriggerRuleSequence(
                TriggerRuleEvent("ledB", "on"),
                TriggerRuleEvent("b", "released"),
            ),
            TriggerRuleSequence(
                TriggerRuleEvent("t", "canceled"),
                TriggerRuleEvent("ledA", "on")))))

    def test_sequence_4_elems_2_events(self):
        expected_trace = TriggerRuleSequence(TriggerRuleEvent("b", "pressed"), TriggerRuleEvent("b", "released"))

        self.assertEqual(expected_trace, get_rules_by_device("b", TriggerRuleSequence(
            TriggerRuleSequence(
                TriggerRuleEvent("ledB", "on"),
                TriggerRuleEvent("b", "pressed"),
            ),
            TriggerRuleSequence(
                TriggerRuleEvent("t", "canceled"),
                TriggerRuleEvent("b", "released")))))

    def test_choice(self):
        expected_trace = TriggerRuleEvent("b", "pressed")

        self.assertEqual(expected_trace,
                         get_rules_by_device("b", TriggerRuleChoice(
                             TriggerRuleEvent("b", "pressed"),
                             TriggerRuleEvent("t", "canceled"))))

        expected_trace = TriggerRuleEvent("t", "canceled")

        self.assertEqual(expected_trace,
                         get_rules_by_device("t", TriggerRuleChoice(
                             TriggerRuleEvent("b", "pressed"),
                             TriggerRuleEvent("t", "canceled"))))

    def test_sequence_choice(self):
        expected_trace = TriggerRuleEvent("b", "released")

        self.assertEqual(expected_trace,
                         get_rules_by_device("b", TriggerRuleSequence(
                             TriggerRuleChoice(
                                 TriggerRuleEvent("b", "released"),
                                 TriggerRuleEvent("t", "canceled")),
                             TriggerRuleEvent("ledA", "on"))))

    def test_sequence_choice_choice(self):
        expected_trace = TriggerRuleEvent("t", "canceled")
        self.assertEqual(expected_trace, get_rules_by_device("t", TriggerRuleSequence(
            TriggerRuleChoice(
                TriggerRuleEvent("b", "released"),
                TriggerRuleChoice(
                    TriggerRuleEvent("ledA", "on"),
                    TriggerRuleEvent("t", "canceled"))),
            TriggerRuleEvent("ledB", "on"))))

        expected_trace = TriggerRuleEvent("b", "released")
        self.assertEqual(expected_trace, get_rules_by_device("b", TriggerRuleSequence(
            TriggerRuleChoice(
                TriggerRuleEvent("b", "released"),
                TriggerRuleChoice(
                    TriggerRuleEvent("ledA", "on"),
                    TriggerRuleEvent("t", "canceled"))),
            TriggerRuleEvent("ledB", "on"))))

    def test_sequence_choice_choice_multiple(self):
        """
        (b.released xor (b.pressed xor t.canceled)); ledB.on
        :return:
        """
        expected_trace = TriggerRuleChoice(TriggerRuleEvent("b", "released"), TriggerRuleEvent("b", "pressed"))
        self.assertEqual(expected_trace, get_rules_by_device("b", TriggerRuleSequence(
            TriggerRuleChoice(
                TriggerRuleEvent("b", "released"),
                TriggerRuleChoice(
                    TriggerRuleEvent("b", "pressed"),
                    TriggerRuleEvent("t", "canceled"))),
            TriggerRuleEvent("ledB", "on"))))

    def test_sequence_choice_choice_multiple_2(self):
        """
        (b.released xor (b.pressed xor t.canceled)); b.pressed
        :return: (b.released xor b.pressed); b.pressed
        """
        expected_trace = TriggerRuleSequence(
            TriggerRuleChoice(
                TriggerRuleEvent("b", "released"),
                TriggerRuleEvent("b", "pressed")),
            TriggerRuleEvent("b", "pressed"))

        self.assertEqual(expected_trace, get_rules_by_device("b", TriggerRuleSequence(
            TriggerRuleChoice(
                TriggerRuleEvent("b", "released"),
                TriggerRuleChoice(
                    TriggerRuleEvent("b", "pressed"),
                    TriggerRuleEvent("t", "canceled"))),
            TriggerRuleEvent("b", "pressed"))))

    def test_left_only(self):
        """
        (b.released; (b.pressed xor t.timeout); (x.timeout xor b.released); (ledA.on xor t.timeout)
        :return: b.released; b.pressed b.released
        """
        expected_trace = TriggerRuleSequence(
            TriggerRuleEvent("b", "released"),
            TriggerRuleSequence(
                TriggerRuleEvent("b", "pressed"),
                TriggerRuleEvent("b", "released")))

        self.assertEqual(
            expected_trace,
            get_rules_by_device("b", TriggerRuleSequence(
                TriggerRuleSequence(
                    TriggerRuleEvent("b", "released"),
                    TriggerRuleSequence(
                        TriggerRuleChoice(
                            TriggerRuleEvent("b", "pressed"),
                            TriggerRuleEvent("x", "timeout")),
                        TriggerRuleChoice(
                            TriggerRuleEvent("x", "timeout"),
                            TriggerRuleEvent("b", "released")))),
                TriggerRuleChoice(
                    TriggerRuleEvent("ledA", "on"),
                    TriggerRuleEvent("t", "timeout")))))

    def test_desk_lamp(self):
        expected_trace = TriggerRuleSequence(TriggerRuleEvent("b", "pressed"), TriggerRuleEvent("b", "released"))
        self.assertEqual(expected_trace,  # standby2
                         get_rules_by_device("b", self.triggers_result[0].trigger_rule))

        self.assertEqual(None, get_rules_by_device("b", self.triggers_result[1].trigger_rule))


if __name__ == '__main__':
    unittest.main()
