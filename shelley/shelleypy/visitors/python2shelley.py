from __future__ import annotations

import logging
import sys
import os
from pathlib import Path
from typing import Any

from astroid import (
    extract_node,
    ClassDef,
    NodeNG
)

from shelley.ast.behaviors import Behaviors
from shelley.ast.components import Components
from shelley.ast.devices import Device
from shelley.ast.events import Events
from shelley.ast.triggers import Triggers
from shelley.shelleypy.visitors import ShelleyPyError
from shelley.shelleypy.visitors.class_decorators import ClassDecoratorsVisitor
from shelley.shelleypy.visitors.method import MethodVisitor

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
        logger.debug(f"System name: {self.device.name}")

        decorators_visitor = ClassDecoratorsVisitor(self.device)
        node.decorators.accept(decorators_visitor)

        for node in node.body:  # process methods
            method_visitor = MethodVisitor(self.device)
            node.accept(method_visitor)

    # def visit_asyncfunctiondef(self, node: AsyncFunctionDef) -> Any:
    #     logger.info(f"Async Method: {node.name}")


def main():
    logger.setLevel(logging.DEBUG)

    # src_path = Path("/app/shelley-examples/micropython_paper_full_example/valve.py")
    src_path = Path("/app/shelley-examples/micropython_paper_full_example/vhandler_full.py")

    with src_path.open() as f:
        tree = extract_node(f.read())

    p2s_visitor = Python2Shelley()

    try:
        tree.accept(p2s_visitor)
    except ShelleyPyError as error:
        logger.error(f"{error.msg} (l. {error.lineno})")
        sys.exit(os.EX_SOFTWARE)

    device = p2s_visitor.device

    from shelley.ast.visitors.pprint import PrettyPrintVisitor
    visitor = PrettyPrintVisitor(components=device.components)
    device.accept(visitor)
    logger.debug(visitor.result.strip())


if __name__ == '__main__':
    main()
