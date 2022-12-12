import pytest

from shelley.ast.visitors.shelley2lark import Shelley2Lark
from shelley.shelleypy.checker.exceptions import ShelleyPyError
from shelley.shelleypy.visitors.python_to_shelley import Python2ShelleyVisitor


def py2shy(py_code: str) -> str:
    device = Python2ShelleyVisitor(external_only=False).py2shy(py_code)

    shy2lark_visitor = Shelley2Lark(components=device.components)
    device.accept(shy2lark_visitor)

    return shy2lark_visitor.result.strip()


def test_duplicated_method() -> None:
    """
    There are two methods in the same class with the same name
    """

    py_src = """
    @system(uses={"v1": "Valve"})
    class App:
        def __init__(self):
            self.v1 = Valve()

        @operation(initial=True, next=["stop"])
        def start(self):
            self.v1.on()
            return "stop"

        @operation(final=True, next=["start"])
        def start(self):
            self.v1.on()                
            return "start"
    """

    with pytest.raises(ShelleyPyError) as exc_info:
        py2shy(py_src)

    assert str(exc_info.value.msg) == ShelleyPyError.DUPLICATED_METHOD
    assert exc_info.value.lineno == 12


