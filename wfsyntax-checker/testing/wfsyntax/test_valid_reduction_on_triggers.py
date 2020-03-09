import unittest

from events import EEvent
from triggers import TriggerRuleSequence, TriggerRuleEvent, TriggerRuleChoice
from _local.devices import is_valid_rule


class TestValidReductionOnTriggers(unittest.TestCase):
    """
    Test triggers that have only one event each
    """

    def setUp(self):
        """
        (first) ledA.on -> (off) ledA.off
        (off) ledA.off -> (on) ledA.on
        (on) ledA.on -> (off) ledA.off
        """

        self.led_behaviours = [
            (EEvent("begin").name, EEvent("on").name),
            (EEvent("on").name, EEvent("off").name),
            (EEvent("off").name, EEvent("on").name)]

    ### EVENTS

    def test_valid_2_events(self):
        rule_a = TriggerRuleEvent("ledA", "on")
        rule_b = TriggerRuleEvent("ledA", "off")

        self.assertTrue(is_valid_rule(rule_a, rule_b, self.led_behaviours))

    def test_invalid_2_events(self):
        rule_a = TriggerRuleEvent("ledA", "on")
        rule_b = TriggerRuleEvent("ledA", "on")

        self.assertFalse(is_valid_rule(rule_a, rule_b, self.led_behaviours))

    ### SEQUENCE
    def test_valid_sequence_left(self):
        rule_a = TriggerRuleSequence(TriggerRuleEvent("ledA", "on"), TriggerRuleEvent("ledA", "off"))
        rule_b = TriggerRuleEvent("ledA", "on")

        self.assertTrue(is_valid_rule(rule_a, rule_b, self.led_behaviours))

    def test_invalid_sequence_left(self):
        rule_a = TriggerRuleSequence(TriggerRuleEvent("ledA", "on"), TriggerRuleEvent("ledA", "off"))
        rule_b = TriggerRuleEvent("ledA", "off")

        self.assertFalse(is_valid_rule(rule_a, rule_b, self.led_behaviours))

    def test_valid_sequence_right(self):
        rule_a = TriggerRuleEvent("ledA", "on")
        rule_b = TriggerRuleSequence(TriggerRuleEvent("ledA", "off"), TriggerRuleEvent("ledA", "on"))

        self.assertTrue(is_valid_rule(rule_a, rule_b, self.led_behaviours))

    def test_invalid_sequence_right(self):
        rule_a = TriggerRuleEvent("ledA", "on")
        rule_b = TriggerRuleSequence(TriggerRuleEvent("ledA", "off"), TriggerRuleEvent("ledA", "off"))

        self.assertFalse(is_valid_rule(rule_a, rule_b, self.led_behaviours))

    ### CHOICE

    def test_valid_choice_left(self):
        """
        R1: on, R2: on, R3: off
        R1 xor R2 -> R3
        R1(on) -> R3(off)
        R2(on) -> R3(off)
        """
        rule_a = TriggerRuleChoice(TriggerRuleEvent("ledA", "on"), TriggerRuleEvent("ledA", "on"))
        rule_b = TriggerRuleEvent("ledA", "off")

        self.assertTrue(is_valid_rule(rule_a, rule_b, self.led_behaviours))

    def test_invalid_choice_left(self):
        """
        R1: off, R2: on, R3: off
        R1 xor R2 -> R3
        R1(off) -> R3(off) INVALID
        R2(on) -> R3(off)
        """
        rule_a = TriggerRuleChoice(TriggerRuleEvent("ledA", "off"), TriggerRuleEvent("ledA", "on"))
        rule_b = TriggerRuleEvent("ledA", "off")

        self.assertFalse(is_valid_rule(rule_a, rule_b, self.led_behaviours))

    def test_valid_choice_right(self):
        """
        R1: off, R2: on, R3: on
        R1 -> R2 xor R3
        R1(off) -> R2(on)
        R1(off) -> R3(on)
        """
        rule_a = TriggerRuleEvent("ledA", "off")
        rule_b = TriggerRuleChoice(TriggerRuleEvent("ledA", "on"), TriggerRuleEvent("ledA", "on"))

        self.assertTrue(is_valid_rule(rule_a, rule_b, self.led_behaviours))

    def test_invalid_choice_right(self):
        """
        R1: off, R2: off, R3: on
        R1 -> R2 xor R3
        R1(off) -> R2(off) INVALID
        R1(off) -> R3(on)
        """
        rule_a = TriggerRuleEvent("ledA", "off")
        rule_b = TriggerRuleChoice(TriggerRuleEvent("ledA", "off"), TriggerRuleEvent("ledA", "on"))

        self.assertFalse(is_valid_rule(rule_a, rule_b, self.led_behaviours))

    ### SEQUENCE, CHOICE

    def test_valid_sequence_choice(self):
        """

        """
        rule_a = TriggerRuleSequence(TriggerRuleEvent("ledA", "on"), TriggerRuleEvent("ledA", "off"))
        rule_b = TriggerRuleChoice(TriggerRuleEvent("ledA", "on"), TriggerRuleEvent("ledA", "on"))

        self.assertTrue(is_valid_rule(rule_a, rule_b, self.led_behaviours))

    def test_invalid_sequence_choice(self):
        """

        """
        rule_a = TriggerRuleSequence(TriggerRuleEvent("ledA", "off"), TriggerRuleEvent("ledA", "off"))
        rule_b = TriggerRuleChoice(TriggerRuleEvent("ledA", "on"), TriggerRuleEvent("ledA", "on"))

        self.assertFalse(is_valid_rule(rule_a, rule_b, self.led_behaviours))

    def test_invalid_sequence_choice2(self):
        """

        """
        rule_a = TriggerRuleSequence(TriggerRuleEvent("ledA", "on"), TriggerRuleEvent("ledA", "off"))
        rule_b = TriggerRuleChoice(TriggerRuleEvent("ledA", "off"), TriggerRuleEvent("ledA", "on"))

        self.assertFalse(is_valid_rule(rule_a, rule_b, self.led_behaviours))

    def test_valid_choice_sequence(self):
        """

        """
        rule_a = TriggerRuleSequence(TriggerRuleEvent("ledA", "on"), TriggerRuleEvent("ledA", "off"))
        rule_b = TriggerRuleChoice(
            TriggerRuleSequence(
                TriggerRuleEvent("ledA", "on"),
                TriggerRuleEvent("ledA", "off")),
            TriggerRuleEvent("ledA", "on"))

        self.assertTrue(is_valid_rule(rule_a, rule_b, self.led_behaviours))

    def test_valid_choice_sequence_2(self):
        """

        """
        rule_a = TriggerRuleChoice(
            TriggerRuleSequence(
                TriggerRuleEvent("ledA", "on"),
                TriggerRuleEvent("ledA", "off")),
            TriggerRuleEvent("ledA", "off"))
        rule_b = TriggerRuleChoice(
            TriggerRuleSequence(
                TriggerRuleEvent("ledA", "on"),
                TriggerRuleEvent("ledA", "off")),
            TriggerRuleEvent("ledA", "on"))

        self.assertTrue(is_valid_rule(rule_a, rule_b, self.led_behaviours))

    def test_invalid_choice_sequence_2(self):
        """

        """
        rule_a = TriggerRuleChoice(
            TriggerRuleSequence(
                TriggerRuleEvent("ledA", "on"),
                TriggerRuleEvent("ledA", "off")),
            TriggerRuleEvent("ledA", "on"))
        rule_b = TriggerRuleChoice(
            TriggerRuleSequence(
                TriggerRuleEvent("ledA", "off"),
                TriggerRuleEvent("ledA", "on")),
            TriggerRuleEvent("ledA", "off"))

        self.assertFalse(is_valid_rule(rule_a, rule_b, self.led_behaviours))


if __name__ == '__main__':
    unittest.main()
