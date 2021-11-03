from __future__ import annotations

from shelley.ast.visitors.triggers import TriggersVisitor
from shelley.ast.triggers import Trigger, Triggers
from shelley.ast.rules import (
    TriggerRuleSequence,
    TriggerRuleChoice,
    TriggerRuleLoop,
    TriggerRuleEvent,
    TriggerRuleFired,
)


class CountCalls(TriggersVisitor):
    count: int

    def __init__(self) -> None:
        self.count = 0

    def visit_trigger_rule_fired(self, element: TriggerRuleFired) -> None:
        pass

    def visit_trigger_rule_event(self, element: TriggerRuleEvent) -> None:
        self.count += 1

    def visit_trigger_rule_sequence(self, element: TriggerRuleSequence) -> None:
        element.left_trigger_rule.accept(self)
        element.right_trigger_rule.accept(self)

    def visit_trigger_rule_choice(self, element: TriggerRuleChoice) -> None:
        element.choices[0].accept(self)
        for choice in element.choices[1:]:
            choice.accept(self)

    def visit_trigger_rule_loop(self, element: TriggerRuleLoop) -> None:
        element.loop.accept(self)

    def visit_trigger(self, element: Trigger) -> None:
        element.trigger_rule.accept(self)

    def visit_triggers(self, element: Triggers) -> None:
        for trigger in element.list():
            trigger.accept(self)

    def __str__(self):
        return self.count
