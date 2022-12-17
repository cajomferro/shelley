from shelley.ast.visitors.shelley2lark import Shelley2Lark
from shelley.shelleypy.visitors.python_to_shelley import Python2ShelleyVisitor


def py2shy(py_code: str) -> str:
    device = Python2ShelleyVisitor(external_only=False).py2shy(py_code)

    shy2lark_visitor = Shelley2Lark(components=device.components)
    device.accept(shy2lark_visitor)

    return shy2lark_visitor.result.strip()


def test_match_ok() -> None:
    """

    """
    app_py = """
    @system(uses={"v": "Valve", "led": "Led"})
    class App:
        def __init__(self):
            self.led = Led()
            self.v = Valve()

        @operation(initial=True, next=["stop", "stop_all", "start"])
        def start(self, use_led=True):
            match self.v.test():
                case "ok":
                    self.v.ok()
                    if use_led:
                        self.led.on()
                        return "stop_all" 
                    else:
                        return "stop" 
                case "error":
                    self.v.error()
                    return "start"

        @operation(final=True, next=["start"])
        def stop(self):
            self.v.off()
            return "start"

        @operation(final=True, next=["start"])
        def stop_all(self):
            self.v.off()
            self.led.off()
            return "start"  
    """

    shy = py2shy(app_py)

    expected_shy = """App (v: Valve, led: Led) {
 start_1 -> stop_all {
  v.test; v.ok; led.on; 
 }
 start_2 -> stop {
  v.test; v.ok; 
 }
 start_3 -> start {
  v.test; v.error; 
 }
 initial start -> start_1, start_2, start_3 {}
 final stop -> start {
  v.off; 
 }
 final stop_all -> start {
  v.off; led.off; 
 }

}
""".strip()

    print(shy)
    assert shy == expected_shy


