import pytest
from shelley.shelleypy.checker.checker import PyVisitor
from shelley.shelleypy.checker.checker import extract_node
from shelley.shelleypy.checker.checker import ShelleyPyError
from shelley.ast.visitors.shelley2lark import Shelley2Lark


def py2shy(py_code: str) -> str:
    svis = PyVisitor(external_only=False)
    svis.find(extract_node(py_code))

    visitor = Shelley2Lark(components=svis.device.components)
    svis.device.accept(visitor)

    return visitor.result.strip()


def test_simple_loop() -> None:
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
  loop {v.on; v.off; }
 }

}
""".strip()

    assert shy == expected_shy


def test_loop_with_return() -> None:
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
                self.v.on()
                wait()
                self.v.off()
            return ""
    """

    with pytest.raises(ShelleyPyError) as exc_info:
        py2shy(app)

    assert str(exc_info.value.msg) == "Return statements are not allowed inside loops!"
    assert exc_info.value.lineno == 10