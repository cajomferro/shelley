from __future__ import annotations

from typing import List

from typing import Optional, Tuple, Dict, Any

from shelley.ast.visitors import Visitor
from shelley.ast.devices import Device
from shelley.ast.actions import Action, Actions
from shelley.ast.events import Event, Events
from shelley.ast.behaviors import Behavior, Behaviors
from shelley.ast.components import Component, Components
from shelley.ast.triggers import Trigger, Triggers
from shelley.ast.rules import (
    TriggerRuleSequence,
    TriggerRuleChoice,
    TriggerRuleLoop,
    TriggerRuleEvent,
    TriggerRuleFired,
)


class Yaml2Lark(Visitor):
    components: Components
    result: str

    def __init__(self, components: Optional[Components] = None):
        if components is None:
            components = Components()
        self.components = components
        self.result = ""

    def visit_trigger_rule_fired(self, element: TriggerRuleFired) -> Any:
        return ""

    def visit_trigger_rule_event(self, element: TriggerRuleEvent) -> Any:
        return "{0}.{1}; ".format(element.component.name, element.event)

    def visit_trigger_rule_sequence(self, element: TriggerRuleSequence) -> Any:
        # self.result += "( "
        result = element.left_trigger_rule.accept(self)
        # result += "; "
        result += element.right_trigger_rule.accept(self)
        # self.result += ") "
        return result

    def visit_trigger_rule_choice(self, element: TriggerRuleChoice) -> Any:
        result = "{"
        for rule in element.choices[0:-1]:
            result += rule.accept(self)
            result += "} + {"
        result += element.choices[-1].accept(self)
        result += "}"

        return result

    def visit_trigger_rule_loop(self, element: TriggerRuleLoop) -> Any:
        pass  # TODO: this was implemented after the Lark parser (there is not loop syntax for the YAML examples)

    def visit_trigger(self, element: Trigger) -> Any:
        # self.result += "    {0}: ".format(element.event.name)
        integration = element.trigger_rule.accept(self)
        # self.result = self.result.strip()
        # self.result += "\n"

        return element.event.name, integration

    def visit_triggers(self, element: Triggers) -> Any:
        triggers = {}
        for trigger in element.list():
            op_name, integration = trigger.accept(self)
            triggers[op_name] = integration
        return triggers

    def visit_component(self, element: Component) -> None:
        device_name = self.components.get_device_name(element.name)
        self.result += "{1}: {0}, ".format(device_name, element.name)

    def visit_components(self, element: Components) -> None:
        for component in element.list():
            component.accept(self)
        self.result = self.result[:-2]  # remove extra ", "
        # self.result += "\n"

    def visit_behaviour(self, element: Behavior) -> None:
        pass

    def visit_behaviors(self, element: Behaviors) -> Dict:
        operations = {}
        for beh in element.list():
            next_op_name_list: List[str] = [beh.e2.name] if beh.e2 is not None else []
            if beh.e1.name not in operations:
                operations[beh.e1.name] = {}
                operations[beh.e1.name]["is_initial"] = beh.e1.is_start
                operations[beh.e1.name]["is_final"] = beh.e1.is_final
                operations[beh.e1.name]["next"] = next_op_name_list
            else:
                operations[beh.e1.name]["next"] += next_op_name_list

        return operations

    def visit_action(self, element: Action) -> None:
        pass

    def visit_actions(self, element: Actions) -> None:
        pass

    def visit_event(self, element: Event) -> None:
        pass

    def visit_events(self, element: Events) -> None:
        pass

    def visit_device(self, element: Device) -> None:

        if len(element.components) > 0:
            self.result = f"{element.name} ("
            element.components.accept(self)
            self.result += f") {{\n"
        else:
            self.result = f"base {element.name} {{\n"

        triggers = element.triggers.accept(self)
        # print(triggers)

        operations = element.behaviors.accept(self)
        for operation in operations:
            initial = " initial" if operations[operation]["is_initial"] else ""
            final = " final" if operations[operation]["is_final"] else ""
            body = (
                ";"
                if len(triggers[operation]) == 0
                else f"{{\n  {triggers[operation]}\n }}"
            )
            self.result += "{0}{1} {2} -> {3} {4}\n".format(
                initial,
                final,
                operation,
                ", ".join(operations[operation]["next"]),
                body,
            )

        self.result += f"\n}}"

    def __str__(self) -> str:
        return self.result


class Shelley2Lark(Visitor):
    components: Components
    result: str

    def __init__(self, components: Optional[Components] = None):
        if components is None:
            components = Components()
        self.components = components
        self.result = ""

    def visit_trigger_rule_fired(self, element: TriggerRuleFired) -> Any:
        return ""

    def visit_trigger_rule_event(self, element: TriggerRuleEvent) -> Any:
        return "{0}.{1}; ".format(element.component.name, element.event)

    def visit_trigger_rule_sequence(self, element: TriggerRuleSequence) -> Any:
        # self.result += "( "
        result = element.left_trigger_rule.accept(self)
        # result += "; "
        result += element.right_trigger_rule.accept(self)
        # self.result += ") "
        return result

    def visit_trigger_rule_choice(self, element: TriggerRuleChoice) -> Any:
        result = "{"
        for rule in element.choices[0:-1]:
            result += rule.accept(self)
            result += "} + {"
        result += element.choices[-1].accept(self)
        result += "}"

        return result

    def visit_trigger_rule_loop(self, element: TriggerRuleLoop) -> Any:
        pass  # TODO: this was implemented after the Lark parser (there is not loop syntax for the YAML examples)

    def visit_trigger(self, element: Trigger) -> Any:
        # self.result += "    {0}: ".format(element.event.name)
        integration = element.trigger_rule.accept(self)
        # self.result = self.result.strip()
        # self.result += "\n"

        return element.event.name, integration

    def visit_triggers(self, element: Triggers) -> Any:
        triggers = {}
        for trigger in element.list():
            op_name, integration = trigger.accept(self)
            triggers[op_name] = integration
        return triggers

    def visit_component(self, element: Component) -> None:
        device_name = self.components.get_device_name(element.name)
        self.result += "{1}: {0}, ".format(device_name, element.name)

    def visit_components(self, element: Components) -> None:
        for component in element.list():
            component.accept(self)
        self.result = self.result[:-2]  # remove extra ", "
        # self.result += "\n"

    def visit_behaviour(self, element: Behavior) -> None:
        pass

    def visit_behaviors(self, element: Behaviors) -> Dict:
        operations = {}
        for beh in element.list():
            next_op_name_list: List[str] = [beh.e2.name] if beh.e2 is not None else []
            if beh.e1.name not in operations:
                operations[beh.e1.name] = {}
                operations[beh.e1.name]["is_initial"] = beh.e1.is_start
                operations[beh.e1.name]["is_final"] = beh.e1.is_final
                operations[beh.e1.name]["next"] = next_op_name_list
            else:
                operations[beh.e1.name]["next"] += next_op_name_list

        return operations

    def visit_action(self, element: Action) -> None:
        pass

    def visit_actions(self, element: Actions) -> None:
        pass

    def visit_event(self, element: Event) -> None:
        pass

    def visit_events(self, element: Events) -> None:
        pass

    def visit_device(self, element: Device) -> None:

        if len(element.components) > 0:
            self.result = f"{element.name} ("
            element.components.accept(self)
            self.result += f") {{\n"
        else:
            self.result = f"base {element.name} {{\n"

        triggers = element.triggers.accept(self)
        # print(triggers)

        operations = element.behaviors.accept(self)
        for operation in operations:
            initial = " initial" if operations[operation]["is_initial"] else ""
            final = " final" if operations[operation]["is_final"] else ""
            body = (
                ";"
                if len(triggers[operation]) == 0
                else f"{{\n  {triggers[operation]}\n }}"
            )
            self.result += "{0}{1} {2} -> {3} {4}\n".format(
                initial,
                final,
                operation,
                ", ".join(operations[operation]["next"]),
                body,
            )

        self.result += f"\n}}"

    def __str__(self) -> str:
        return self.result
