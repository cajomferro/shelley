import logging
from pathlib import Path

from astroid import extract_node

from shelley.ast.devices import Device
from shelley.shelleypy.visitors import VisitorHelper
from shelley.shelleypy.visitors.python_to_shelley import Python2ShelleyVisitor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("shelleypy")


def python2shelley(src_path: Path, external_only=False) -> Device:
    with src_path.open() as f:
        tree = extract_node(f.read())
    visitor_helper = VisitorHelper(external_only=external_only)
    p2s_visitor = Python2ShelleyVisitor(visitor_helper)
    tree.accept(p2s_visitor)
    return visitor_helper.device


def main():
    """
    Use only for debug purposes
    """
    logger.setLevel(logging.INFO)

    # src_path = Path("/app/shelley-examples/micropython_paper_full_example/valve.py")
    # src_path = Path("/app/shelley-examples/micropython_paper_full_example/vhandler_full.py")
    src_path = Path("test.py")

    device: Device = python2shelley(src_path)

    from shelley.ast.visitors.pprint import PrettyPrintVisitor
    visitor = PrettyPrintVisitor(components=device.components)
    device.accept(visitor)
    logger.info(visitor.result.strip())


if __name__ == '__main__':
    main()
