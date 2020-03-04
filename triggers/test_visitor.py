import unittest
from ast.rules import TriggerRuleSequence, TriggerRuleChoice, TriggerRuleEvent, PrettyPrint, CheckWFSyntax


class TestRules(unittest.TestCase):
    def test_pretty_print(self):
        rules = TriggerRuleSequence(
            TriggerRuleChoice(
                TriggerRuleEvent("b", "released"),
                TriggerRuleChoice(
                    TriggerRuleEvent("ledA", "on"),
                    TriggerRuleEvent("t", "canceled"))
            ),
            TriggerRuleEvent("ledB", "on")
        )
        visitor = PrettyPrint()
        rules.accept(visitor)

        self.assertEqual("((b.released  xor (ledA.on  xor t.canceled )) ; ledB.on )", visitor.rules)

    def test_check_wf_syntax(self):
        trigger = TriggerRuleSequence(
            TriggerRuleChoice(
                TriggerRuleEvent("b", "released"),
                TriggerRuleChoice(
                    TriggerRuleEvent("ledA", "on"),
                    TriggerRuleEvent("t", "canceled"))
            ),
            TriggerRuleEvent("ledB", "on")
        )
        visitor = CheckWFSyntax()
        trigger.accept(visitor)

        # self.assertEqual("((b.released  xor (ledA.on  xor t.canceled )) ; ledB.on )", visitor.rule)


if __name__ == '__main__':
    unittest.main()
