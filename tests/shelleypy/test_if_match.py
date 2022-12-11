from shelley.ast.devices import Device
from shelley.ast.visitors.shelley2lark import Shelley2Lark
from shelley.shelleypy.checker.checker import extract_node
from shelley.shelleypy.checker.optimize import optimize as fun_optimize
from shelley.shelleypy.visitors.python_to_shelley import Python2ShelleyVisitor
from shelley.shelleypy.visitors import VisitorHelper


def py2shy(py_code: str) -> str:
    visitor_helper = VisitorHelper(external_only=False)
    p2s_visitor = Python2ShelleyVisitor(visitor_helper)
    extract_node(py_code).accept(p2s_visitor)

    fun_optimize(visitor_helper.device)

    visitor = Shelley2Lark(components=visitor_helper.device.components)
    visitor_helper.device.accept(visitor)

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
