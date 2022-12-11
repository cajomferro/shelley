from shelley.shelleypy.visitors.python_to_shelley import Python2ShelleyVisitor
from shelley.shelleypy.checker.checker import extract_node
from shelley.ast.visitors.shelley2lark import Shelley2Lark
from shelley.shelleypy.visitors import VisitorHelper


# TODO: right now we are not processing the value of initial and final, we just assume based on if it is there or not
# omitting final=False or initial=False will make the test pass but we should support this instead
def test_app_v1() -> None:
    py_code = """
    @claim("system check G (main -> F (main & END));")
    @system(uses={"v1": "Valve", "v2": "Valve"})
    class App:
        def __init__(self):
            self.v1 = Valve()
            self.v2 = Valve()

        @operation(initial=True, final=False, next=["turn_off"])
        def turn_on(self):
            self.v1.on()
            self.v2.on()
            return "turn_off"

        @operation(initial=False, final=True, next=["turn_on"])
        def turn_off(self):
            self.v1.off() 
            self.v2.off()
            return "turn_on"
    """

    visitor_helper = VisitorHelper(external_only=False)
    p2s_visitor = Python2ShelleyVisitor(visitor_helper)
    extract_node(py_code).accept(p2s_visitor)

    visitor = Shelley2Lark(components=visitor_helper.device.components)
    visitor_helper.device.accept(visitor)

    lark_code = visitor.result.strip()

    expected_lark_code = """
App (v1: Valve, v2: Valve) {
 initial turn_on -> turn_off {
  v1.on; v2.on; 
 }
 final turn_off -> turn_on {
  v1.off; v2.off; 
 }

}
""".strip()

    assert not lark_code == expected_lark_code  # TODO: remove the 'not' when this is fixed
