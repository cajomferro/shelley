from __future__ import annotations

import logging
from typing import Any

from astroid import (
    Call,
    Decorators,
    NodeNG
)

from shelley.ast.devices import Device

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("shelleypy")


class MethodDecoratorsVisitor(NodeNG):
    def __init__(self):
        super().__init__()
        self.decorator = None

    def visit_decorators(self, node: Decorators) -> Any:
        for node in node.nodes:
            node.accept(self)

    def visit_call(self, node: Call) -> Any:
        logger.info(f"Method decorator: {node.func.name}")
        decorator_name = node.func.name
        match decorator_name:
            case "operation":
                decorator = {
                    "type": "operation",
                    "initial": False,
                    "final": False,
                    "next": [],
                }
                for kw in node.keywords:
                    match kw.arg:
                        case "initial":
                            decorator["initial"] = True
                        case "final":
                            decorator["final"] = True
                        case "next":
                            decorator["next"] = [
                                op.value for op in kw.value.elts
                            ]
                self.decorator = decorator
