from pathlib import Path
from shelley.ast.devices import Device as ShelleyDevice
from shelley.parsers import shelley_lark_parser
from shelley.ast.visitors.count_calls import CountCalls

EXAMPLES_PATH = Path() / Path(__file__).parent.parent / "shelley-examples"


def test_sectors():
    path = EXAMPLES_PATH / "thesis_aquamote_example" / "sectors.shy"
    device: ShelleyDevice = shelley_lark_parser.parse(path)

    visitor = CountCalls()
    device.triggers.accept(visitor)

    assert visitor.count == 12


def test_controller():
    path = EXAMPLES_PATH / "thesis_aquamote_example" / "controller.shy"
    device: ShelleyDevice = shelley_lark_parser.parse(path)

    visitor = CountCalls()
    device.triggers.accept(visitor)

    assert visitor.count == 19


def test_valve():
    path = EXAMPLES_PATH / "thesis_aquamote_example" / "valve.shy"
    device: ShelleyDevice = shelley_lark_parser.parse(path)

    visitor = CountCalls()
    device.triggers.accept(visitor)

    assert visitor.count == 0
