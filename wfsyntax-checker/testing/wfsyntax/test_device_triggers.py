import unittest

from testing.creator import create_device_led, create_device_button, create_device_timer, create_device_desk_lamp
from testing.creator import create_device_desk_lamp_duplicated_trigger
from events.checker import check as check_events
from behaviours.checker import check as check_behaviours
from components.checker import check as check_components
from triggers.checker import check as check_triggers, TriggersListDuplicatedError
from events import GenericEvent, EEvent, IEvent
from triggers import TriggerRule, TriggerRuleSequence


class TestDeskLamp(unittest.TestCase):
    def test_is_valid(self):
        d_led = create_device_led()
        d_button = create_device_button()
        d_timer = create_device_timer()
        d_desk_lamp = create_device_desk_lamp(d_led, d_button, d_timer)

        declared_devices = {
            d_led.name: d_led,
            d_button.name: d_button,
            d_timer.name: d_timer,
        }

        # check(d_desk_lamp, declared_devices, composite=True) --> should I have a dedicated check for device?

        # check_actions(d_desk_lamp.actions) --> this device has no actions!

        declared_i_events, declared_e_events = check_events(
            d_desk_lamp.get_all_events())  # type: Tuple[List[IEvent, EEvent]]
        self.assertEqual(0, len(declared_i_events))  # desk lamp has no internal events
        self.assertEqual(5, len(declared_e_events))  # desk lamp has 5 external events

        behaviours_result = []  # type: List[Tuple[GenericEvent, GenericEvent]]
        check_behaviours(d_desk_lamp.behaviours, d_desk_lamp.actions, declared_i_events, declared_e_events,
                         behaviours_result)
        self.assertEqual(6, len(behaviours_result))  # desk lamp has 6 behaviours

        # this is a composite device, check also components and triggers

        declared_components = check_components(d_desk_lamp.components, d_desk_lamp.uses,
                                               declared_devices)  # type: Dict[str, Device]
        self.assertEqual(4, len(declared_components))  # desk lamp has 4 components

        triggers_result = []  # type: List[Trigger]
        check_triggers(d_desk_lamp.triggers, declared_e_events, declared_components, triggers_result)
        self.assertEqual(5, len(triggers_result))  # desk lamp has 4 triggers
        self.assertEqual(triggers_result[0].event, GenericEvent('standby2'))
        self.assertEqual(triggers_result[1].event, GenericEvent('standby1'))
        self.assertEqual(triggers_result[2].event, GenericEvent('level2'))
        self.assertEqual(triggers_result[3].event, GenericEvent('level1'))
        self.assertEqual(triggers_result[4].event, GenericEvent('begin'))
        self.assertTrue(type(triggers_result[0].trigger_rule) is TriggerRuleSequence)  # TODO: add more tests here!!

    def test_duplicated_trigger(self):
        d_led = create_device_led()
        d_button = create_device_button()
        d_timer = create_device_timer()
        d_desk_lamp = create_device_desk_lamp_duplicated_trigger(d_led, d_button, d_timer)

        declared_devices = {
            d_led.name: d_led,
            d_button.name: d_button,
            d_timer.name: d_timer,
        }

        declared_i_events, declared_e_events = check_events(
            d_desk_lamp.get_all_events())  # type: Tuple[List[IEvent, EEvent]]
        self.assertEqual(0, len(declared_i_events))  # desk lamp has no internal events
        self.assertEqual(5, len(declared_e_events))  # desk lamp has 5 external events

        behaviours_result = []  # type: List[Tuple[GenericEvent, GenericEvent]]
        check_behaviours(d_desk_lamp.behaviours, d_desk_lamp.actions, declared_i_events, declared_e_events,
                         behaviours_result)
        self.assertEqual(6, len(behaviours_result))  # desk lamp has 6 behaviours

        # this is a composite device, check also components and triggers

        declared_components = check_components(d_desk_lamp.components, d_desk_lamp.uses,
                                               declared_devices)  # type: Dict[str, Device]
        self.assertEqual(4, len(declared_components))  # desk lamp has 4 components

        triggers_result = []  # type: List[TriggerRule]
        with self.assertRaises(TriggersListDuplicatedError) as context:
            check_triggers(d_desk_lamp.triggers, declared_e_events, declared_components, triggers_result)


if __name__ == '__main__':
    unittest.main()
