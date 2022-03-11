
import shelley.ast.triggers
from shelley.shelleypy.checker.checker import PyVisitor
from shelley.shelleypy.checker.checker import extract_node
from shelley.ast.visitors.shelley2lark import Shelley2Lark
from shelley.ast.devices import Device as ShelleyDevice
from shelley.ast.behaviors import Behaviors
from shelley.ast.behaviors import Behavior
from shelley.ast.events import Event, Events
from shelley.ast.triggers import Triggers, Trigger
from shelley.ast.rules import TriggerRuleChoice
from typing import Mapping, List
from shelley.parsers.shelley_lark_parser import parser as lark_parser, ShelleyLanguage
from shelley.shelleypy.checker.optimize import optimize

def py2shelley_device(py_code: str) -> ShelleyDevice:
    svis = PyVisitor(external_only=False)
    svis.find(extract_node(py_code))

    return svis.device

def test_v1() -> None:
    """
    try_open_2 and try_open_3 can be "merged"
    """

    original_device_shy = """Controller (a: Valve, b: Valve) {
 try_open_1 -> close {
  a.test; a.open; b.test; b.open; 
 }
 try_open_2 -> fail {
  a.test; a.open; b.test; b.clean; a.close; 
 }
 try_open_3 -> fail {
  a.test; a.clean; 
 }
 initial try_open -> try_open_1, try_open_2, try_open_3 {}
 final fail -> try_open {}
 final close -> try_open {
  a.close; b.close; 
 }
}
    """

    device: ShelleyDevice = ShelleyLanguage().transform(lark_parser.parse(original_device_shy))

    optimize(device)

    new_device_lark = shelley2lark(device)

    expected_device_shy = """Controller (a: Valve, b: Valve) {
 try_open_1 -> close {
  a.test; a.open; b.test; b.open; 
 }
 try_open_2 -> fail {
  {a.test; a.open; b.test; b.clean; a.close; } + {a.test; a.clean; }
 }
 initial try_open -> try_open_1, try_open_2 {}
 final fail -> try_open {}
 final close -> try_open {
  a.close; b.close; 
 }

}"""

    assert expected_device_shy == new_device_lark


def test_v2() -> None:
    """
    try_open_2 and try_open_3 can be "merged", fail does not have next
    """

    original_device_shy = """Controller (a: Valve, b: Valve) {
 try_open_1 -> close {
  a.test; a.open; b.test; b.open; 
 }
 try_open_2 -> fail {
  a.test; a.open; b.test; b.clean; a.close; 
 }
 try_open_3 -> fail {
  a.test; a.clean; 
 }
 initial try_open -> try_open_1, try_open_2, try_open_3 {}
 final fail -> {} # no next here!
 final close -> try_open {
  a.close; b.close; 
 }
}
    """

    device: ShelleyDevice = ShelleyLanguage().transform(lark_parser.parse(original_device_shy))

    optimize(device)

    new_device_lark = shelley2lark(device)

    expected_device_shy = """Controller (a: Valve, b: Valve) {
 try_open_1 -> close {
  a.test; a.open; b.test; b.open; 
 }
 try_open_2 -> fail {
  {a.test; a.open; b.test; b.clean; a.close; } + {a.test; a.clean; }
 }
 initial try_open -> try_open_1, try_open_2 {}
 final fail ->  {}
 final close -> try_open {
  a.close; b.close; 
 }

}"""

    assert expected_device_shy == new_device_lark


def test_v3() -> None:
    """
    try_open_1, try_open_2 and try_open_3 can be "merged", fail does not have next
    """

    original_device_shy = """Controller (a: Valve, b: Valve) {
 try_open_1 -> fail {
  a.test; a.open; b.test; b.open; 
 }
 try_open_2 -> fail {
  a.test; a.open; b.test; b.clean; a.close; 
 }
 try_open_3 -> fail {
  a.test; a.clean; 
 }
 initial try_open -> try_open_1, try_open_2, try_open_3 {}
 final fail -> {} # no next here!
}
    """

    device: ShelleyDevice = ShelleyLanguage().transform(lark_parser.parse(original_device_shy))

    optimize(device)

    new_device_lark = shelley2lark(device)

    expected_device_shy = """Controller (a: Valve, b: Valve) {
 try_open_1 -> fail {
  {{a.test; a.open; b.test; b.open; } + {a.test; a.open; b.test; b.clean; a.close; }} + {a.test; a.clean; }
 }
 initial try_open -> try_open_1 {}
 final fail ->  {}

}"""

    assert expected_device_shy == new_device_lark


def test_v4() -> None:
    """
    try_open_1, try_open_2 can be "merged", fail does not have next
    """

    original_device_shy = """Controller (a: Valve, b: Valve) {
 try_open_1 -> fail {
  a.test; a.open; b.test; b.open; 
 }
 try_open_2 -> fail {
  a.test; a.open; b.test; b.clean; a.close;
 }
 initial try_open -> try_open_1, try_open_2 {}
 initial open -> try_open_2 {}
 final fail -> {} # no next here!
}"""

    device: ShelleyDevice = ShelleyLanguage().transform(lark_parser.parse(original_device_shy))

    optimize(device)

    new_device_lark = shelley2lark(device)

    expected_device_shy = """Controller (a: Valve, b: Valve) {
 try_open_1 -> fail {
  {a.test; a.open; b.test; b.open; } + {a.test; a.open; b.test; b.clean; a.close; }
 }
 initial try_open -> try_open_1 {}
 initial open -> try_open_1 {}
 final fail ->  {}

}"""

    assert  new_device_lark == expected_device_shy


def shelley2lark(device: ShelleyDevice):
    visitor = Shelley2Lark(components=device.components)
    device.accept(visitor)

    return visitor.result.strip()

