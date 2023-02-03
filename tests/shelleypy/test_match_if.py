from shelley.ast.visitors.shelley2lark import Shelley2Lark
from shelley.shelleypy.visitors.python_to_shelley import Python2ShelleyVisitor


def py2shy(py_code: str) -> str:
    device = Python2ShelleyVisitor(external_only=False).py2shy(py_code)

    shy2lark_visitor = Shelley2Lark(components=device.components)
    device.accept(shy2lark_visitor)

    return shy2lark_visitor.result.strip()


def test_match_if_v1() -> None:
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


def test_match_if_v2() -> None:
    """
    """

    py_code = """
    @claim("integration check (!b.open) W a.open;")  # equivalent to: ((! b.open) U a.open) | (G (! b.open))
    @claim("subsystem b check G (open -> X close);")  # equivalent to: ((! b.open) U a.open) | (G (! b.open))
    @system(uses={"a": "Valve", "b": "Valve"})
    class ValveHandler:

        def __init__(self):
            self.a = Valve()
            self.b = Valve()

        @operation(initial=True, next=["close", "close_all", "fail"])
        def try_open(self, fallback_b_valve=True):
            match self.a.test():
                case "open":
                    self.a.open()
                    print("Valve a opened!")
                    if fallback_b_valve:
                        match self.b.test():
                            case "open":
                                self.b.open()
                                return "close_all"
                            case "clean":
                                self.b.clean()
                                return "close"
                    else:
                        return "close"
                case "clean":
                    self.a.clean()
                    return "fail" 

        @operation(final=True, next=["try_open"])
        def fail(self):
            print("Valve a failed!")
            return "try_open"

        @operation(final=True, next=["try_open"])
        def close(self):
            self.a.close()
            print("Valve a closed!")
            return "try_open"

        @operation(final=True, next=["try_open"])
        def close_all(self):
            self.a.close()
            self.b.close()
            return "try_open"
    """

    shy = py2shy(py_code)

    expected_shy = """ValveHandler (a: Valve, b: Valve) {
 try_open_1 -> close_all {
  a.test; a.open; b.test; b.open; 
 }
 try_open_2 -> close {
  a.test; a.open; b.test; b.clean; 
 }
 try_open_3 -> close {
  a.test; a.open; 
 }
 try_open_4 -> fail {
  a.test; a.clean; 
 }
 initial try_open -> try_open_1, try_open_2, try_open_3, try_open_4 {}
 final fail -> try_open {}
 final close -> try_open {
  a.close; 
 }
 final close_all -> try_open {
  a.close; b.close; 
 }

 integration check ((! b.open) U a.open) | (G (! b.open));

 subsystem b check G (open -> (X close));

}
""".strip()

    assert shy == expected_shy


def test_match_if_v3() -> None:
    """
    """

    py_code = """
    @system(uses={"v1": "Valve"})
    class VHandler:
        def __init__(self):
            self.v1 = Valve()

        @operation(initial=True, next=["all_tries_failed", "close"])
        def main(self, mytest=False):
            self.v1.init()
            match self.v1.test():
                case "ok":
                    self.v1.ok()
                    if mytest:
                        self.v1.on()
                    return "close"
                case "error1":
                    self.v1.error1()
                # case "error2":
                #    self.v1.error2()
            self.v1.clean()
            return "all_tries_failed"

        @operation(final=True, next=[""])
        def all_tries_failed(self):
            return ""


        @operation(final=True, next=[""])
        def close(self):
            self.v1.off()
            return ""
    """

    shy = py2shy(py_code)

    expected_shy = """VHandler (v1: Valve) {
 main_1 -> close {
  v1.init; v1.test; v1.ok; {v1.on;} + {} 
 }
 main_2 -> all_tries_failed {
  v1.init; v1.test; v1.error1; v1.clean; 
 }
 initial main -> main_1, main_2 {}
 final all_tries_failed ->  {}
 final close ->  {
  v1.off; 
 }

}
""".strip()

    assert shy == expected_shy

def test_match_if_v4() -> None:
    """
    """

    py_code = """
    @system(uses={"v1": "Valve"})
    class VHandler:
        def __init__(self):
            self.v1 = Valve()
    
        @operation(initial=True, next=["all_tries_failed", "close"])
        def main(self, mytest=False):
            self.v1.init()
            match self.v1.test():
                case "ok":
                    self.v1.ok()
                    if mytest:
                        self.v1.on()
                    return "close"
                case "error1":
                    self.v1.error1()
                case "error2":
                    self.v1.error2()
            self.v1.clean()
            return "all_tries_failed"
    
        @operation(final=True, next=[""])
        def all_tries_failed(self):
            return ""
    
    
        @operation(final=True, next=[""])
        def close(self):
            self.v1.off()
            return ""
    """

    shy = py2shy(py_code)

    expected_shy = """VHandler (v1: Valve) {
 main_1 -> close {
  v1.init; v1.test; v1.ok; {v1.on;} + {} 
 }
 main_2 -> all_tries_failed {
  v1.init; v1.test; {v1.error1;} + {v1.error2;} v1.clean; 
 }
 initial main -> main_1, main_2 {}
 final all_tries_failed ->  {}
 final close ->  {
  v1.off; 
 }

}
""".strip()

    assert shy == expected_shy