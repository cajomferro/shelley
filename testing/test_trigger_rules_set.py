import unittest

from testing.creator import create_device_led, create_device_button, create_device_timer, create_device_desk_lamp
from events.checker import check as check_events
from behaviours.checker import check as check_behaviours
from components.checker import check as check_components
from triggers.checker import check as check_triggers
from events import GenericEvent, EEvent, IEvent
from triggers import TriggerRuleSequence, TriggerRuleEvent, TriggerRuleChoice
from devices import get_devices_as_set


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

        declared_i_events, declared_e_events = check_events(d_desk_lamp.get_all_events())  # type: Tuple[List[IEvent, EEvent]]

        behaviours_result = []  # type: List[Tuple[GenericEvent, GenericEvent]]
        check_behaviours(d_desk_lamp.behaviours, d_desk_lamp.actions, declared_i_events, declared_e_events,
                         behaviours_result)

        declared_components = check_components(d_desk_lamp.components, d_desk_lamp.uses,
                                               declared_devices)  # type: Dict[str, Device]

        self.triggers_result = []  # type: List[Trigger]
        check_triggers(d_desk_lamp.triggers, declared_e_events, declared_components, self.triggers_result)

        self.declared_components = declared_components

    def test_sequence(self):
        self.assertEqual([{'b', 't'}],
                         get_devices_as_set(TriggerRuleSequence(
                             TriggerRuleEvent("b", "released"),
                             TriggerRuleEvent("t", "canceled")), self.declared_components))

    def test_sequence_3_elems(self):
        self.assertEqual([{'b', 't', 'ledA'}],
                         get_devices_as_set(
                             TriggerRuleSequence(
                                 TriggerRuleEvent("b", "released"),
                                 TriggerRuleSequence(
                                     TriggerRuleEvent("t", "canceled"),
                                     TriggerRuleEvent("ledA", "on")
                                 )
                             ), self.declared_components))

    def test_sequence_4_elems(self):
        self.assertEqual([{'ledB', 'b', 't', 'ledA'}],
                         get_devices_as_set(
                             TriggerRuleSequence(
                                 TriggerRuleSequence(
                                     TriggerRuleEvent("ledB", "on"),
                                     TriggerRuleEvent("b", "released"),
                                 ),
                                 TriggerRuleSequence(
                                     TriggerRuleEvent("t", "canceled"),
                                     TriggerRuleEvent("ledA", "on")
                                 )
                             ), self.declared_components))

    def test_choice(self):
        self.assertEqual([{'b'}, {'t'}],
                         get_devices_as_set(
                             TriggerRuleChoice(
                                 TriggerRuleEvent("b", "released"),
                                 TriggerRuleEvent("t", "canceled")
                             ), self.declared_components))

    def test_sequence_choice(self):
        self.assertEqual([{'b', 'ledA'}, {'t', 'ledA'}],
                         get_devices_as_set(
                             TriggerRuleSequence(
                                 TriggerRuleChoice(
                                     TriggerRuleEvent("b", "released"),
                                     TriggerRuleEvent("t", "canceled")
                                 ),
                                 TriggerRuleEvent("ledA", "on"))

                             , self.declared_components))

    def test_sequence_choice_choice(self):
        self.assertEqual([{'b', 'ledB'}, {'ledA', 'ledB'}, {'t', 'ledB'}],
                         get_devices_as_set(
                             TriggerRuleSequence(
                                 TriggerRuleChoice(
                                     TriggerRuleEvent("b", "released"),
                                     TriggerRuleChoice(
                                         TriggerRuleEvent("ledA", "on"),
                                         TriggerRuleEvent("t", "canceled"))
                                 ),
                                 TriggerRuleEvent("ledB", "on")
                             )
                             , self.declared_components))

    def test_desk_lamp(self):
        self.assertEqual(
            [{'b', 't', 'ledB', 'ledA'}, {'b', 't', 'ledA', 'ledB'}, {'t', 'ledB', 'ledA'}, {'t', 'ledA', 'ledB'}],
            get_devices_as_set(self.triggers_result[0].trigger_rule, self.declared_components))

        self.assertEqual([{'t', 'ledB'}],
                         get_devices_as_set(self.triggers_result[1].trigger_rule, self.declared_components))


if __name__ == '__main__':
    unittest.main()
