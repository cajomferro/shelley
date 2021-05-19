from __future__ import annotations

import yaml
from pathlib import Path
from shelley import parsers

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
        for behaviour in element.list():
            op_name = behaviour.e1.name
            next_op_name = behaviour.e2.name
            if op_name not in operations:
                operations[op_name] = {}
                operations[op_name]["is_initial"] = behaviour.e1.is_start
                operations[op_name]["is_final"] = behaviour.e1.is_final
                operations[op_name]["next"] = [next_op_name]
            else:
                operations[op_name]["next"].append(next_op_name)

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


def translate(yaml_source: Path, lark_source: Path):
    shelley_device = parsers.get_shelley_from_yaml(yaml_source)
    visitor = Yaml2Lark(components=shelley_device.components)
    shelley_device.accept(visitor)

    lark_code = visitor.result.strip()
    # print(lark_code)

    with lark_source.open("w") as f:
        f.write(lark_code)


def main():
    import sys

    if len(sys.argv) < 2:
        print("Please provide a valid source path! Usage: yaml2lark PATH")
        sys.exit(255)

    yaml_path = Path(sys.argv[1])
    lark_path = Path(sys.argv[1][:-4] + ".shy")
    # print(yaml_path)
    # print(lark_path)
    translate(yaml_path, lark_path)


if __name__ == "__main__":
    main()
