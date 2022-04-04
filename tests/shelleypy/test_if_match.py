import pytest
from pathlib import Path
from shelley.shelleypy.checker.checker import PyVisitor
from shelley.shelleypy.checker.checker import fun_optimize
from shelley.shelleypy.checker.checker import extract_node
from shelley.ast.visitors.shelley2lark import Shelley2Lark
from shelley.ast.devices import Device


def py2shy(py_code: str) -> str:
    svis = PyVisitor(external_only=False)
    svis.find(extract_node(py_code))
    device: Device = svis.device
    fun_optimize(device)

    visitor = Shelley2Lark(components=svis.device.components)
    device.accept(visitor)

    return visitor.result.strip()


def test_app_v1() -> None:
    """
    Simple return inside if/else
    """

    app_py = """@system(uses={"c": "Controller"})
class App:
    def __init__(self):
        self.c = Controller()

    @operation(initial=True, final=True, next=["run"])
    def run(self, TEST_MODE=False):
        self.c.boot()
        if TEST_MODE is False:
            match self.c.try_update():
                case "c.update_ok":
                    self.c.update_ok()
                    self.c.follow_new_plan()
                    return "run"
                case "update_error":
                    self.c.update_error()
                    self.c.follow_default_plan()
                    return "run"
        else:
            self.c.sleep() # TODO: this generates wrong code
            return "run"
    """

    shy = py2shy(app_py)

    expected_shy = """App (c: Controller) {
 final run_1 -> run {
  {{c.boot; c.try_update; c.update_ok; c.follow_new_plan; } + {c.boot; c.try_update; c.update_error; c.follow_default_plan; }} + {c.boot; c.sleep; }
 }
 initial run -> run_1 {}

}
""".strip()

    print(shy)

    assert shy == expected_shy

