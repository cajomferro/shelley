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

from lark import Lark
from shelley.parsers.ltlf_lark_parser import LTLParser
from shelley.parsers import ltlf_lark_parser

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
logger = logging.getLogger("pyshelley")


class ShelleyClassDecoratorsVisitor(NodeNG):
    def __init__(self, device: Device, external_only=False):
        super().__init__()
        self.device = device
        self.external_only = external_only
        self.ltlf_parser = Lark.open(
            "ltlf_grammar.lark", rel_to=ltlf_lark_parser.__file__, start="formula"
        ).parse

    def visit_decorators(self, node: Decorators) -> Any:
        logger.info(node)
        for node in node.nodes:
            node.accept(self)

    def visit_call(self, node: Call) -> Any:
        logger.info(f"Call: {node.func.name}")
        decorator_name = node.func.name
        match decorator_name:
            case "claim":
                claim: str = node.args[0].value
                logger.debug(f"Claim: {claim}")
                claim = claim.removesuffix(";")
                if "system check" in claim and self.external_only:
                    claim = claim.removeprefix("system check")
                    formula = LTLParser().transform(self.ltlf_parser(claim))
                    self.device.system_formulae.append(formula)
                elif "integration check" in claim and not self.external_only:
                    claim = claim.removeprefix("integration check")
                    formula = LTLParser().transform(self.ltlf_parser(claim))
                    self.device.integration_formulae.append(formula)
                elif claim.startswith("subsystem") and not self.external_only:
                    parts = claim.split(" ")  # separate by spaces
                    name = parts[1]  # get subystem name from formula
                    parts = parts[3:]  # remove 'subsystem XX check' from string
                    claim = " ".join(parts)  # re-join by spaces
                    formula = LTLParser().transform(self.ltlf_parser(claim))
                    self.device.subsystem_formulae.append((name, formula))
            case "system":
                for kw in node.keywords:
                    match kw.arg:
                        case "uses":
                            if not self.external_only:
                                for name, type in kw.value.items:
                                    self.device.components.create(
                                        name.value, type.value
                                    )
                                    self.device.uses = discover_uses(
                                        self.device.components
                                    )  # TODO: melhorar isto?


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

        decorators_visitor = ShelleyClassDecoratorsVisitor(self.device)
        node.decorators.accept(decorators_visitor)

        for node in node.body:
            node.accept(self)

    def visit_functiondef(self, node: FunctionDef) -> Any:
        logger.info(f"Method: {node.name}")

    def visit_asyncfunctiondef(self, node: AsyncFunctionDef) -> Any:
        logger.info(f"Async Method: {node.name}")


def main():
    src_path = Path("/app/shelley-examples/micropython_paper_full_example/vhandler_full.py")

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
