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


def test_app_v1() -> None:
    """
    Simple return inside if/else
    """

    app_v1_py = """
    @system(uses={"v1": "Valve", "v2": "Valve"})
    class App:
        def __init__(self):
            self.v1 = Valve()
            self.v2 = Valve()

        @operation(initial=True, next=["stop_v1", "stop_v2"])
        def main(self):
            if x:
                self.v1.on()
                return "stop_v1" 
            else:
                self.v2.on()
                return "stop_v2"

        @operation(final=True, next=["main"])    
        def stop_v1(self):
            self.v1.off()
            return "main"

        @operation(final=True, next=["main"])
        def stop_v2(self):
            self.v2.off()
            return "main"
    """

    shy = py2shy(app_v1_py)

    expected_shy = """App (v1: Valve, v2: Valve) {
 main_1 -> stop_v1 {
  v1.on; 
 }
 main_2 -> stop_v2 {
  v2.on; 
 }
 initial main -> main_1, main_2 {}
 final stop_v1 -> main {
  v1.off; 
 }
 final stop_v2 -> main {
  v2.off; 
 }

}
""".strip()

    print(shy)

    assert shy == expected_shy


def test_app_v2() -> None:
    """
    Simple return inside if/else
    """

    app = """
    @system(uses={"v1": "Valve", "v2": "Valve"})
    class App:
        def __init__(self):
            self.v1 = Valve()
            self.v2 = Valve()

        @operation(initial=True, next=["main", "stop_v1", "stop_v2"])
        def main(self):
            if x:
                if x:
                    if x:
                        self.v1.on()
                        return "stop_v1" 
                else:
                    return "main"
            else:
                self.v2.on()
                return "stop_v2"

        @operation(final=True, next=["main"])    
        def stop_v1(self):
            self.v1.off()
            return "main"

        @operation(final=True, next=["main"])
        def stop_v2(self):
            self.v2.off()
            return "main"
    """

    shy = py2shy(app)

    expected_shy = """App (v1: Valve, v2: Valve) {
 main_1 -> stop_v1 {
  v1.on; 
 }
 main_2 -> main {}
 main_3 -> stop_v2 {
  v2.on; 
 }
 initial main -> main_1, main_2, main_3 {}
 final stop_v1 -> main {
  v1.off; 
 }
 final stop_v2 -> main {
  v2.off; 
 }

}
""".strip()

    print(shy)

    assert shy == expected_shy