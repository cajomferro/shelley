from __future__ import annotations

import logging
from typing import Any

from astroid import (
    Call,
    Decorators,
    NodeNG
)
from lark import Lark

from shelley.ast.devices import Device, discover_uses
from shelley.parsers import ltlf_lark_parser
from shelley.parsers.ltlf_lark_parser import LTLParser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pyshelley")


class ClassDecoratorsVisitor(NodeNG):
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


