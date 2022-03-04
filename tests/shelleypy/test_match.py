import pytest
from pathlib import Path
from shelley.shelleypy.checker.checker import PyVisitor
from shelley.shelleypy.checker.checker import extract_node
from shelley.ast.visitors.shelley2lark import Shelley2Lark


def py2shy(py_code: str) -> str:
    svis = PyVisitor(external_only=False)
    svis.find(extract_node(py_code))

    visitor = Shelley2Lark(components=svis.device.components)
    svis.device.accept(visitor)

    return visitor.result.strip()


def test_match_ok() -> None:
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

    #print(shy)

    assert shy == expected_shy


# TODO: currently is not possible to detect code outside a match so it will generate as if it was another case branch
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
                    self.v1.on()
                    return "" 
                case "error":
                    self.v2.on()
                    return ""
            self.v1.on()
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
 main_3 ->  {
  v1.on; v1.test; v2.on; 
 }
 initial main -> main_1, main_2, main_3 {}

}
""".strip()

    #print(shy)

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