from __future__ import annotations

import logging

from typing import Optional, Tuple, Dict, Any, List

from pathlib import Path

from astroid import (
    parse,
    extract_node,
    AsyncFunctionDef,
    FunctionDef,
    Expr,
    Match,
    Await,
    Call,
    If,
    Return,
    ClassDef,
    Decorators,
    AnnAssign,
    MatchSequence,
    MatchCase,
    MatchValue,
    Const,
    For,
    NodeNG
)

from shelley.shelleypy.visitors.class_decorators import ClassDecoratorsVisitor
from shelley.shelleypy.visitors.method import MethodVisitor

from shelley.ast.devices import Device, discover_uses
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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("shelleypy")


class Python2Shelley(NodeNG):
    device: Device

    def __init__(self, external_only=False):
        super().__init__()
        self.device = Device(
            name="",
            events=Events(),
            behaviors=Behaviors(),
            triggers=Triggers(),
            components=Components(),
        )
        self.external_only = external_only

    def visit_classdef(self, node: ClassDef) -> Any:
        self.device.name = node.name
        logger.info(f"System name: {self.device.name}")

        decorators_visitor = ClassDecoratorsVisitor(self.device)
        node.decorators.accept(decorators_visitor)

        for node in node.body:  # process methods
            method_visitor = MethodVisitor(self.device)
            node.accept(method_visitor)

    # def visit_asyncfunctiondef(self, node: AsyncFunctionDef) -> Any:
    #     logger.info(f"Async Method: {node.name}")


def main():
    src_path = Path("/app/shelley-examples/micropython_paper_full_example/valve.py")
    # src_path = Path("/app/shelley-examples/micropython_paper_full_example/vhandler_full.py")

    with src_path.open() as f:
        tree = extract_node(f.read())

    p2s_visitor = Python2Shelley()
    tree.accept(p2s_visitor)

    device = p2s_visitor.device

    from shelley.ast.visitors.pprint import PrettyPrintVisitor
    visitor = PrettyPrintVisitor(components=device.components)
    device.accept(visitor)
    logger.info(visitor.result.strip())


if __name__ == '__main__':
    main()
