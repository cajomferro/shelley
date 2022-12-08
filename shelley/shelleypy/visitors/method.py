from __future__ import annotations

from typing import Any, Dict

import logging
import copy

from astroid import (
    FunctionDef,
    NodeNG
)

from shelley.ast.devices import Device
from shelley.ast.events import Events, Event
from shelley.ast.triggers import Triggers, TriggerRule
from shelley.ast.rules import (
    TriggerRuleSequence,
    TriggerRuleEvent,
    TriggerRuleFired,
    TriggerRuleChoice,
    TriggerRuleLoop,
)
from shelley.shelleypy.visitors.method_decorators import MethodDecoratorsVisitor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("shelleypy")


class MethodVisitor(NodeNG):
    def __init__(self, device: Device, external_only=False):
        self.device = device
        self.external_only = external_only
        super().__init__()

    def visit_functiondef(self, node: FunctionDef) -> Any:
        logger.info(f"Method: {node.name}")
        decorator = self._get_decorator(node.decorators)

        if decorator:
            self._process_operation(node, decorator)

    def _process_operation(self, node: FunctionDef, decorator: Dict):
        if (
                len(self.device.uses) == 0
        ) or self.external_only:  # base system, do not inspect body
            self._create_operation(
                node.name,
                decorator["initial"],
                decorator["final"],
                decorator["next"],
                TriggerRuleFired(),
            )
        else:
            pass
            # TODO:

    def _create_operation(self, name, is_initial, is_final, next_ops_list, rules):
        current_operation: Event = self.device.events.create(
            name,
            is_start=is_initial,
            is_final=is_final,
        )

        if len(next_ops_list) == 0:
            self.device.behaviors.create(
                copy.copy(current_operation)
            )  # operation without next operations

        for next_op in next_ops_list:
            self.device.behaviors.create(
                copy.copy(current_operation),
                Event(
                    name=next_op,
                    is_start=False,
                    is_final=True,
                ),
            )

        self.device.triggers.create(copy.copy(current_operation), copy.copy(rules))

    @staticmethod
    def _get_decorator(decorators):
        if decorators is None:
            logger.debug(f"Skipping. This method is not annotated as an operation!")
            return None

        decorators_visitor = MethodDecoratorsVisitor()
        decorators.accept(decorators_visitor)
        decorator = decorators_visitor.decorator

        if decorator is None:
            logger.debug(f"Skipping. This method is not annotated as an operation!")
            return None

        if not decorator["type"] == "operation":
            logger.debug(f"Skipping. This method is not annotated as an operation!")
            return None

        return decorator
