import unittest
from events import GenericEvent, EEvent, IEvent
from triggers import TriggerRuleSequence, TriggerRuleEvent, TriggerRuleChoice
from devices import pred


class TestSequentialEvents(unittest.TestCase):
    """
    Test triggers that have only one event each
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
        predecessors = pred(EEvent("e1"), "ledA", self.behaviours, self.triggers)
        self.assertEqual(['begin'], [str(elem) for elem in predecessors])

    def test_ledA_e2(self):
        predecessors = pred(EEvent("e2"), "ledA", self.behaviours, self.triggers)
        self.assertEqual(['e1'], [str(elem) for elem in predecessors])

    def test_ledA_e3(self):
        predecessors = pred(EEvent("e3"), "ledA", self.behaviours, self.triggers)
        self.assertEqual(['e2'], [str(elem) for elem in predecessors])


if __name__ == '__main__':
    unittest.main()
