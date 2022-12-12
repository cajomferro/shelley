import logging
from pathlib import Path

from shelley.ast.devices import Device
from shelley.shelleypy.visitors.python_to_shelley import Python2ShelleyVisitor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("shelleypy")


def python2shelley(src_path: Path, external_only=False) -> Device:
    return Python2ShelleyVisitor(external_only=external_only).py2shy(src_path)


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
