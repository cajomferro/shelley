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
    Simple return inside if/else
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


def test_code_outside_match() -> None:
    """
    Simple return inside if/else
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
  v1.on; 
 }
 initial main -> main_1, main_2, main_3 {}

}
""".strip()

    #print(shy)

    assert shy == expected_shy
