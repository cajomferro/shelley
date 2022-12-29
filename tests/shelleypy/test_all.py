import pytest

from shelley.ast.visitors.shelley2lark import Shelley2Lark
from shelley.shelleypy.checker.exceptions import ShelleyPyError
from shelley.shelleypy.visitors.python_to_shelley import Python2ShelleyVisitor


def py2shy(py_code: str) -> str:
    device = Python2ShelleyVisitor(external_only=False).py2shy(py_code)

    shy2lark_visitor = Shelley2Lark(components=device.components)
    device.accept(shy2lark_visitor)

    return shy2lark_visitor.result.strip()


def test_all_v1() -> None:
    """
    Based on shelley-examples/thesis_running_example_python_v2/vhandler.py
    """

    app = """
    @system(uses={"a": "Valve", "b": "Valve", "led": "LED"})
    class App:
        def __init__(self):
            self.a = Valve()
            self.b = Valve()
            self.led = LED()
    
        @operation(initial=True, next=["try_open", "close_a", "close_b"])
        def try_open(self, use_a=True, blink_led=True):
            if use_a:
                match self.a.test():
                    case "open":
                        self.a.open()
                        if blink_led:
                            for i in range(10):
                                self.led.on()
                                self.led.off()
                            return "close_a"
                        else:
                            return "close_a"
                    case "clean":
                        self.a.clean()
                        return "try_open"
            else:
                match self.b.test():
                    case "open":
                        self.b.open()
                        return "close_b"
                    case "clean":
                        self.b.clean()
                        return "try_open"
    
        @operation(final=True, next=["try_open"])
        def close_a(self):
            self.a.close()
            return "try_open"
    
        @operation(final=True, next=["try_open"])
        def close_b(self):
            self.b.close()
            return "try_open"
    """

    shy = py2shy(app)

    expected_shy = """
App (a: Valve, b: Valve, led: LED) {
 try_open_1 -> close_a {
  a.test; a.open; loop {led.on; led.off; }
 }
 try_open_2 -> close_a {
  a.test; a.open; 
 }
 try_open_3 -> try_open {
  a.test; a.clean; 
 }
 try_open_4 -> close_b {
  b.test; b.open; 
 }
 try_open_5 -> try_open {
  b.test; b.clean; 
 }
 initial try_open -> try_open_1, try_open_2, try_open_3, try_open_4, try_open_5 {}
 final close_a -> try_open {
  a.close; 
 }
 final close_b -> try_open {
  b.close; 
 }

}
""".strip()

    assert shy == expected_shy


