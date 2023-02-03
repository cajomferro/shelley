from shelley.ast.visitors.shelley2lark import Shelley2Lark
from shelley.shelleypy.visitors.python_to_shelley import Python2ShelleyVisitor


def py2shy(py_code: str) -> str:
    device = Python2ShelleyVisitor(external_only=False).py2shy(py_code)

    shy2lark_visitor = Shelley2Lark(components=device.components)
    device.accept(shy2lark_visitor)

    return shy2lark_visitor.result.strip()


def test_match_v1() -> None:
    """

    """

    app_py = """
    @system(uses={"v1": "Valve", "v2": "Valve"})
    class App:
        def __init__(self):
            self.v1 = Valve()
            self.v2 = Valve()

        @operation(initial=True, next=[])
        def main(self):
            match self.v1.test():
                case "ok":
                    self.v1.on()
                    return "" 
                case "error":
                    self.v2.on()
                    return ""
    """

    shy = py2shy(app_py)

    expected_shy = """App (v1: Valve, v2: Valve) {
 main_1 ->  {
  v1.test; v1.on; 
 }
 main_2 ->  {
  v1.test; v2.on; 
 }
 initial main -> main_1, main_2 {}

}
""".strip()

    # print(shy)

    assert shy == expected_shy

def test_match_v2() -> None:
    """

    """

    app_py = """
    @system(uses={"v1": "Valve", "v2": "Valve"})
    class App:
        def __init__(self):
            self.v1 = Valve()
            self.v2 = Valve()

        @operation(initial=True, next=["main"])
        def main(self):
            match self.v1.test():
                case "ok":
                    self.v1.on()
                    return "main" 
                case "error":
                    self.v2.on()
                    return "main"
    """

    shy = py2shy(app_py)

    expected_shy = """App (v1: Valve, v2: Valve) {
 main_1 -> main {
  v1.test; v1.on; 
 }
 main_2 -> main {
  v1.test; v2.on; 
 }
 initial main -> main_1, main_2 {}

}
""".strip()

    # print(shy)

    assert shy == expected_shy

def test_match_v3() -> None:
    """

    """

    app_py = """
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

    shy = py2shy(app_py)

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

    # print(shy)

    assert shy == expected_shy


def test_match_v4() -> None:
    """

    """

    app_py = """
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
                    self.v1.on()
                case "error":
                    self.v1.error()
                    return "close"
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

    shy = py2shy(app_py)

    expected_shy = """VHandler (v1: Valve) {
 main_1 -> close {
  v1.init; v1.test; v1.error; 
 }
 main_2 -> all_tries_failed {
  v1.init; v1.test; v1.ok; v1.on; v1.clean; 
 }
 initial main -> main_1, main_2 {}
 final all_tries_failed ->  {}
 final close ->  {
  v1.off; 
 }

}
""".strip()

    # print(shy)

    assert shy == expected_shy


def test_match_v5() -> None:
    """

    """

    app_py = """
    @system(uses={"v1": "Valve"})
    class VHandler:
        def __init__(self):
            self.v1 = Valve()
    
        @operation(initial=True, next=["close", "error"])
        def main(self):
            self.v1.init()
            match self.v1.test():
                case "ok":
                    self.v1.ok()
                    self.v1.on()
                    return "close"
                case "error":
                    self.v1.error()
                    return "error"
    
        @operation(final=True, next=[""])
        def error(self):
            self.v1.clean()
            return ""
            
        @operation(final=True, next=[""])
        def close(self):
            self.v1.off()
            return ""            
    """

    shy = py2shy(app_py)

    expected_shy = """VHandler (v1: Valve) {
 main_1 -> close {
  v1.init; v1.test; v1.ok; v1.on; 
 }
 main_2 -> error {
  v1.init; v1.test; v1.error; 
 }
 initial main -> main_1, main_2 {}
 final error ->  {
  v1.clean; 
 }
 final close ->  {
  v1.off; 
 }

}
""".strip()

    # print(shy)

    assert shy == expected_shy

def test_code_outside_match() -> None:
    """
    self.v1.on() is outside case and should be ignored
    """

    app_py = """
    @system(uses={"v1": "Valve", "v2": "Valve"})
    class App:
        def __init__(self):
            self.v1 = Valve()
            self.v2 = Valve()

        @operation(initial=True, next=[])
        def main(self):
            match self.v1.test():
                case "ok":
                    self.v1.ok()
                    self.v1.on()
                    return "" 
                case "error":
                    self.v1.error()
                    self.v2.on()
                    return ""
            self.v1.on()
            return ""
    """

    shy = py2shy(app_py)

    expected_shy = """App (v1: Valve, v2: Valve) {
 main_1 ->  {
  v1.test; v1.ok; v1.on; 
 }
 main_2 ->  {
  v1.test; v1.error; v2.on; 
 }
 main_3 ->  {
  v1.test; v1.on; 
 }
 initial main -> main_1, main_2, main_3 {}

}
""".strip()

    print(shy)
    assert shy == expected_shy


def test_nested_match() -> None:
    """
    Match inside match (based on paper_example_app_v2/controller.py)
    """

    app_py = """
    @system(uses={"a": "Valve", "b": "Valve"})
    class Controller:
        def __init__(self):
            self.a = Valve()
            self.b = Valve()
    
        @operation(initial=True, next=["close", "fail"])
        def try_open(self):
            match self.a.test():
                case "open":
                    self.a.open()
                    match self.b.test():
                        case "open":
                            self.b.open()
                            return "close"
                        case "clean":
                            self.b.clean()
                            self.a.close()
                            return "fail"
                case "clean":
                    self.a.clean()
                    return "fail"
    
        @operation(final=True, next=["try_open"])
        def fail(self):
            print("Failed to open valves")
            return "try_open"
    
        @operation(final=True, next=["try_open"])
        def close(self):
            self.a.close()
            self.b.close()
            return "try_open"
    """

    shy = py2shy(app_py)

    expected_shy = """Controller (a: Valve, b: Valve) {
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
""".strip()

    # print(shy)

    assert shy == expected_shy


def test_nested_match_v2() -> None:
    """
    # TODO: fix this bug!
    """

    app_py = """
    @system(uses={"a": "Valve", "b": "Valve"})
    class Controller:
        def __init__(self):
            self.a = Valve()
            self.b = Valve()
    
        @operation(initial=True, next=["try_open", "when_a", "when_b"])
        def try_open(self):
            match self.a.test():
                case "open":
                    self.a.open()
                    return "when_a"
                case "clean":
                    self.a.clean()
                    match self.b.test():
                        case "open":
                            self.b.open()
                            return "when_b"
                        case "clean":
                            self.b.clean()
                            return "try_open"
    
        @operation(final=True, next=["try_open"])
        def when_a(self):
            self.a.close()
            return "try_open"
    
        @operation(final=True, next=["try_open"])
        def when_b(self):
            self.b.close()
            return "try_open"
    """

    shy = py2shy(app_py)

    expected_shy = """Controller (a: Valve, b: Valve) {
 try_open_1 -> when_a {
  a.test; a.open; 
 }
 try_open_2 -> when_b {
  a.test; a.clean; b.test; b.open; 
 }
 try_open_3 -> try_open {
  a.test; a.clean; b.test; b.clean; 
 }
 initial try_open -> try_open_1, try_open_2, try_open_3 {}
 final when_a -> try_open {
  a.close; 
 }
 final when_b -> try_open {
  b.close; 
 }

}
""".strip()

    # print(shy)
    assert shy == expected_shy

def test_nested_match_v3() -> None:
    """
    """

    py_code = """
@system(uses={"a": "Valve", "b": "Valve"})
class App:
    def __init__(self):
        self.a = Valve()
        self.b = Valve()

    @operation(initial=True, next=["try_open", "when_a", "when_b"])
    def try_open(self):
        match self.a.test():
            case "open":
                self.a.open()
                return "when_a"
            case "clean":
                self.a.clean()
                match self.b.test():
                    case "xalala":
                        self.b.xalala()
                    case "open":
                        self.b.open()
                        return "when_b"
                    case "clean":
                        self.b.clean()
                        return "try_open"
                self.a.cenas()
                #return "try_open"
            case "omg":
                self.a.omg()
        return "try_open"

    @operation(final=True, next=["try_open"])
    def when_a(self):
        self.a.close()
        return "try_open"

    @operation(final=True, next=["try_open"])
    def when_b(self):
        self.b.close()
        return "try_open"
    """

    shy = py2shy(py_code)

    expected_shy = """App (a: Valve, b: Valve) {
 try_open_1 -> when_a {
  a.test; a.open; 
 }
 try_open_2 -> when_b {
  a.test; a.clean; b.test; b.open; 
 }
 try_open_3 -> try_open {
  a.test; a.clean; b.test; b.clean; 
 }
 try_open_4 -> try_open {
  a.test; {a.clean; b.test; b.xalala; a.cenas;} + {a.omg;} 
 }
 initial try_open -> try_open_1, try_open_2, try_open_3, try_open_4 {}
 final when_a -> try_open {
  a.close; 
 }
 final when_b -> try_open {
  b.close; 
 }

}
""".strip()

    assert shy == expected_shy

def test_nested_match_v4() -> None:
    """
    """

    py_code = """
@system(uses={"a": "Valve", "b": "Valve"})
class App:
    def __init__(self):
        self.a = Valve()
        self.b = Valve()

    @operation(initial=True, next=["try_open", "when_a", "when_b"])
    def try_open(self):
        match self.a.test():
            case "open":
                self.a.open()
                return "when_a"
            case "clean":
                self.a.clean()
                match self.b.test():
                    case "xalala":
                        self.b.xalala()
                    case "open":
                        self.b.open()
                        return "when_b"
                    case "clean":
                        self.b.clean()
                        return "try_open"
                self.a.cenas()
                return "try_open"
            case "omg":
                self.a.omg()
        return "try_open"

    @operation(final=True, next=["try_open"])
    def when_a(self):
        self.a.close()
        return "try_open"

    @operation(final=True, next=["try_open"])
    def when_b(self):
        self.b.close()
        return "try_open"
    """

    shy = py2shy(py_code)

    expected_shy = """App (a: Valve, b: Valve) {
 try_open_1 -> when_a {
  a.test; a.open; 
 }
 try_open_2 -> when_b {
  a.test; a.clean; b.test; b.open; 
 }
 try_open_3 -> try_open {
  a.test; a.clean; b.test; b.clean; 
 }
 try_open_4 -> try_open {
  a.test; a.clean; b.test; b.xalala; a.cenas; 
 }
 try_open_5 -> try_open {
  a.test; a.omg; 
 }
 initial try_open -> try_open_1, try_open_2, try_open_3, try_open_4, try_open_5 {}
 final when_a -> try_open {
  a.close; 
 }
 final when_b -> try_open {
  b.close; 
 }

}
""".strip()

    assert shy == expected_shy