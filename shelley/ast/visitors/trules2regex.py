from __future__ import annotations
from typing import Dict, Set, Tuple, List

from .triggers import TriggersVisitor
from shelley.ast.triggers import Trigger, Triggers
from shelley.ast.rules import TriggerRuleSequence, TriggerRuleChoice, TriggerRuleEvent, TriggerRuleFired
from karakuri.regular import Regex, Char, Concat, Union, Void


class TRules2RegexVisitor(TriggersVisitor):
    regex_dict = None  # type: Dict[str, Regex]
    current_regex = None  # type: Regex

    def __init__(self):
        self.regex_dict = dict()
        self.current_regex = Void

    def visit_trigger_rule_fired(self, element: TriggerRuleFired) -> None:
        # self.current_regex = Nil() # TODO: como processar o fired?
        pass

    def visit_trigger_rule_event(self, element: TriggerRuleEvent) -> None:
        self.current_regex = Char(str(element))

    def visit_trigger_rule_sequence(self, element: TriggerRuleSequence) -> None:
        element.left_trigger_rule.accept(self)
        left = self.current_regex
        element.right_trigger_rule.accept(self)
        right = self.current_regex
        self.current_regex = Concat(left, right)

    def visit_trigger_rule_choice(self, element: TriggerRuleChoice) -> None:
        element.left_trigger_rule.accept(self)
        left = self.current_regex
        element.right_trigger_rule.accept(self)
        right = self.current_regex
        self.current_regex = Union(left, right)

    def visit_trigger(self, element: Trigger) -> None:
        element.trigger_rule.accept(self)
        self.regex_dict[element.event.name] = self.current_regex

    def visit_triggers(self, element: Triggers) -> None:
        for trigger in element.list():
            trigger.accept(self)

    def __str__(self):
        return self.regex_dict

#
# class CountStatesVisitor(Visitor):
#     visited_events = None  # type: List[str]
#     # state_names = None # type: List[Tuple[str, str, str]]
#     state_names = None  # type: Dict
#     counter = None  # type: int
#
#     def __init__(self):
#         self.counter = 1
#         self.visited_events = []
#         self.state_names = {0: []}
#
#     def visit_trigger_rule_fired(self, element: TriggerRuleFired) -> None:
#         pass
#
#     def visit_trigger_rule_event(self, element: TriggerRuleEvent) -> None:
#         pass
#
#     def visit_trigger_rule_sequence(self, element: TriggerRuleSequence) -> None:
#         pass
#
#     def visit_trigger_rule_choice(self, element: TriggerRuleChoice) -> None:
#         pass
#
#     def visit_component(self, element: Component) -> None:
#         pass
#
#     def visit_behaviour(self, element: Behavior) -> None:
#         if element.e1.name not in self.visited_events and element.e2.name not in self.visited_events:
#             self.visited_events.append(element.e1.name)
#             self.visited_events.append(element.e2.name)
#             #self.state_names.append("{0}_{1}".format(element.e1.name, element.e2.name))
#             self.state_names[self.counter] = []
#             self.state_names[self.counter].append(element.e1.name)
#             self.counter += 1
#
#
#     def visit_action(self, element: Action) -> None:
#         pass
#
#     def visit_ievent(self, element: IEvent) -> None:
#         pass
#
#     def visit_eevent(self, element: EEvent) -> None:
#         pass
#
#     def visit_device(self, element: Device) -> None:
#         for b in element.behaviors:
#             b.accept(self)
