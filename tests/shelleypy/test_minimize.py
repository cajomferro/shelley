from shelley.ast.devices import Device as ShelleyDevice
from shelley.ast.visitors.shelley2lark import Shelley2Lark
from shelley.parsers.shelley_lark_parser import parser as lark_parser, ShelleyLanguage
from shelley.shelleypy.checker.optimize import optimize
from shelley.shelleypy.visitors.python_to_shelley import Python2ShelleyVisitor


def py2shelley_device(py_code: str) -> ShelleyDevice:
    return Python2ShelleyVisitor(external_only=False).py2shy(py_code)


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
  {a.test; a.open; b.test; b.clean; a.close;} + {a.test; a.clean;} 
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
  {a.test; a.open; b.test; b.clean; a.close;} + {a.test; a.clean;} 
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
  {{a.test; a.open; b.test; b.open;} + {a.test; a.open; b.test; b.clean; a.close;}} + {a.test; a.clean;} 
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
  {a.test; a.open; b.test; b.open;} + {a.test; a.open; b.test; b.clean; a.close;} 
 }
 initial try_open -> try_open_1 {}
 initial open -> try_open_1 {}
 final fail ->  {}

}"""

    assert new_device_lark == expected_device_shy


def test_v5() -> None:
    """
    try_open_1 and try_open_2 CANNOT be "merged", fail does not have next
    """

    original_device_shy = """Controller (a: Valve, b: Valve) {
 try_open_1 -> fail, fail2 {
  a.test; a.open; b.test; b.open; 
 }
 try_open_2 -> fail {
  a.test; a.open; b.test; b.clean; a.close;
 }
 initial try_open -> try_open_1, try_open_2 {}
 initial open -> try_open_2 {}
 final fail -> {} # no next here!
 final fail2 -> { # no next here!
    a.test;
 }
}"""

    device: ShelleyDevice = ShelleyLanguage().transform(lark_parser.parse(original_device_shy))

    optimize(device)

    new_device_lark = shelley2lark(device)

    expected_device_shy = """Controller (a: Valve, b: Valve) {
 try_open_1 -> fail, fail2 {
  a.test; a.open; b.test; b.open; 
 }
 try_open_2 -> fail {
  a.test; a.open; b.test; b.clean; a.close; 
 }
 initial try_open -> try_open_1, try_open_2 {}
 initial open -> try_open_2 {}
 final fail ->  {}
 final fail2 ->  {
  a.test; 
 }

}"""

    assert new_device_lark == expected_device_shy


def test_v6() -> None:
    """
    This test should not pass but at the moment I am not optimising cases where right side is empty
    """

    original_device_shy = """Controller (a: Valve, b: Valve) {
 try_open_1 -> fail, fail2 {
  a.test; a.open; b.test; b.open; 
 }
 try_open_2 -> fail {
  a.test; a.open; b.test; b.clean; a.close;
 }
 final fail -> {a.test;} # no next here!
 final fail2 -> {a.test;} # no next here!
}"""

    device: ShelleyDevice = ShelleyLanguage().transform(lark_parser.parse(original_device_shy))

    optimize(device)

    new_device_lark = shelley2lark(device)

    expected_device_shy = """Controller (a: Valve, b: Valve) {
 try_open_1 -> fail, fail2 {
  a.test; a.open; b.test; b.open; 
 }
 try_open_2 -> fail {
  a.test; a.open; b.test; b.clean; a.close; 
 }
 final fail ->  {
  a.test; 
 }
 final fail2 ->  {
  a.test; 
 }

}"""

    assert new_device_lark == expected_device_shy


def test_v7() -> None:
    """
    fail and fail2 can be "merged", fail does not have next
    """

    original_device_shy = """Controller (a: Valve, b: Valve) {
 try_open_1 -> fail, fail2 {
  a.test; a.open; b.test; b.open;
 }
 try_open_2 -> fail {
  a.test; a.open; b.test; b.clean; a.close;
 }
 initial final test -> {}
 final fail -> test {a.test;} # no next here!
 final fail2 -> test {a.test;} # no next here!
}"""

    device: ShelleyDevice = ShelleyLanguage().transform(lark_parser.parse(original_device_shy))

    optimize(device)

    new_device_lark = shelley2lark(device)

    expected_device_shy = """Controller (a: Valve, b: Valve) {
 try_open_1 -> fail, fail2 {
  a.test; a.open; b.test; b.open; 
 }
 try_open_2 -> fail {
  a.test; a.open; b.test; b.clean; a.close; 
 }
 initial final test ->  {}
 final fail -> test {
  a.test; 
 }
 final fail2 -> test {
  a.test; 
 }

}"""

    assert new_device_lark == expected_device_shy


def shelley2lark(device: ShelleyDevice):
    visitor = Shelley2Lark(components=device.components)
    device.accept(visitor)

    return visitor.result.strip()
