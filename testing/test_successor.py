import unittest
from unittest.mock import MagicMock

from testing.creator import create_device_led, create_device_button, create_device_timer, create_device_desk_lamp
from events.checker import check as check_events
from behaviours.checker import check as check_behaviours
from components.checker import check as check_components
from triggers.checker import check as check_triggers
from events import GenericEvent, EEvent, IEvent
from triggers import TriggerRuleSequence, TriggerRuleEvent, TriggerRuleChoice
from devices import Device, succ


class TestSequentialEvents(unittest.TestCase):
    """
    Test triggers with sequential events only
    """

    def setUp(self):
        """
        begin -> e1 -> e2 -> e3 -> e1
        """
        self.behaviours = [
            (EEvent("begin"), EEvent("e1")),
            (EEvent("e1"), EEvent("e2")),
            (EEvent("e2"), EEvent("e3")),
            (EEvent("e3"), EEvent("e1"))]

        self.triggers = {
            EEvent("begin"): TriggerRuleSequence(TriggerRuleEvent("ledA", "begin"), TriggerRuleEvent("ledB", "begin")),
            EEvent("e1"): TriggerRuleSequence(TriggerRuleEvent("ledA", "on"), TriggerRuleEvent("ledB", "off")),
            EEvent("e2"): TriggerRuleSequence(TriggerRuleEvent("ledA", "off"), TriggerRuleEvent("ledB", "on")),
            EEvent("e3"): TriggerRuleEvent("ledB", "on")
        }

    ### EVENTS

    def test_ledA_e1(self):
        successors = succ(EEvent("begin"), "ledA", self.behaviours, self.triggers)
        self.assertEqual(['e1'], [str(elem) for elem in successors])

    def test_ledA_e2(self):
        successors = succ(EEvent("e1"), "ledA", self.behaviours, self.triggers)
        self.assertEqual(['e2'], [str(elem) for elem in successors])

    def test_ledA_e3(self):
        successors = succ(EEvent("e3"), "ledA", self.behaviours, self.triggers)
        self.assertEqual(["e1"], [str(elem) for elem in successors])


if __name__ == '__main__':
    unittest.main()
