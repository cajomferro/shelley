import pytest

from shelley.ast.visitors.shelley2lark import Shelley2Lark
from shelley.shelleypy.checker.exceptions import ShelleyPyError
from shelley.shelleypy.visitors.python_to_shelley import Python2ShelleyVisitor


def py2shy(py_code: str) -> str:
    device = Python2ShelleyVisitor(external_only=False).py2shy(py_code)

    shy2lark_visitor = Shelley2Lark(components=device.components)
    device.accept(shy2lark_visitor)

    return shy2lark_visitor.result.strip()


def test_while() -> None:
    """

    """

    app = """
    @claim("system check G (main -> F (main & END));")
    @system(uses={"v": "Valve"})
    class App:
        def __init__(self):
            self.v = Valve()

        @operation(initial=True, final=True, next=[])
        def main(self):
            i = 0
            while i < 10:
                self.v.on()
                wait(10)
                self.v.off()
                wait(10)
                i += 1
            return ""
    """

    shy = py2shy(app)

    expected_shy = """
App (v: Valve) {
 initial final main ->  {
  loop{v.on; v.off;} 
 }

}
""".strip()

    # print(shy)
    assert shy == expected_shy


def test_for() -> None:
    """

    """

    app = """
    @claim("system check G (main -> F (main & END));")
    @system(uses={"v": "Valve"})
    class App:
        def __init__(self):
            self.v = Valve()

        @operation(initial=True, final=True, next=[])
        def main(self):
            for _ in range(10):
                self.v.on()
                wait()
                self.v.off()
            return ""
    """

    shy = py2shy(app)

    expected_shy = """
App (v: Valve) {
 initial final main ->  {
  loop{v.on; v.off;} 
 }

}
""".strip()

    assert shy == expected_shy


def test_nested_for() -> None:
    """

    """

    app = """
    @system(uses={"v1": "Valve", "v2": "Valve"})
    class App:
        def __init__(self):
            self.v1 = Valve()
            self.v2 = Valve()

        @operation(initial=True, final=True, next=[])
        def main(self):
            for _ in range(10):
                self.v1.on()
                for _ in range(10):
                    self.v2.on()
                    wait(10)
                    self.v2.off()
                    wait(10)
                self.v1.off()
            return ""
    """

    shy = py2shy(app)

    expected_shy = """
App (v1: Valve, v2: Valve) {
 initial final main ->  {
  loop{v1.on; loop{v2.on; v2.off;} v1.off;} 
 }

}
""".strip()
    # print(shy)
    assert shy == expected_shy


def test_loop_with_return_v1() -> None:
    """

    """

    app = """
    @claim("system check G (main -> F (main & END));")
    @system(uses={"v": "Valve"})
    class App:
        def __init__(self):
            self.v = Valve()

        @operation(initial=True, final=True, next=[])
        def main(self):
            for i in range(10):
                return ""
    """

    shy = py2shy(app)

    expected_shy = """
App (v: Valve) {
 initial final main ->  {}

}
""".strip()
    # print(shy)
    assert shy == expected_shy


def test_loop_with_return_v2() -> None:
    """

    """

    app = """
    @claim("system check G (main -> F (main & END));")
    @system(uses={"v": "Valve"})
    class App:
        def __init__(self):
            self.v = Valve()

        @operation(initial=True, final=True, next=[])
        def main(self):
            for i in range(10):
                if i == 5:
                    self.v.on()
                    return ""
                else:
                    return ""
    """

    shy = py2shy(app)

    expected_shy = """
App (v: Valve) {
 final main_1 ->  {
  loop{} v.on; 
 }
 final main_2 ->  {
  loop{} 
 }
 initial main -> main_1, main_2 {}

}
    """.strip()
    assert shy == expected_shy
