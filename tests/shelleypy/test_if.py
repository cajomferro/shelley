import pytest

from shelley.ast.visitors.shelley2lark import Shelley2Lark
from shelley.shelleypy.checker.exceptions import ShelleyPyError
from shelley.shelleypy.visitors.python_to_shelley import Python2ShelleyVisitor


def py2shy(py_code: str) -> str:
    device = Python2ShelleyVisitor(external_only=False).py2shy(py_code)

    shy2lark_visitor = Shelley2Lark(components=device.components)
    device.accept(shy2lark_visitor)

    return shy2lark_visitor.result.strip()


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

    # print(shy)

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


def test_app_v3() -> None:
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
 main_3 -> main {}
 main_4 -> stop_v2 {
  v2.on; 
 }
 initial main -> main_1, main_2, main_3, main_4 {}
 final stop_v1 -> main {
  v1.off; 
 }
 final stop_v2 -> main {
  v2.off; 
 }

}
""".strip()

    # print(shy)

    assert shy == expected_shy


def test_elif() -> None:
    """
    Simple return inside if/else
    """

    app_v1_py = """
    @system(uses={"v1": "Valve", "v2": "Valve", "v3": "Valve"})
    class App:
        def __init__(self):
            self.v1 = Valve()
            self.v2 = Valve()
            self.v3 = Valve()

        @operation(initial=True, next=["stop_v1", "stop_v2", "stop_v3"])
        def main(self, valve_name):
            if valve_name == 'v1':
                self.v1.on()
                return "stop_v1" 
            elif valve_name == 'v2':
                self.v2.on()
                return "stop_v2"
            else:
                self.v3.on()
                return "stop_v3"

        @operation(final=True, next=["main"])    
        def stop_v1(self):
            self.v1.off()
            return "main"

        @operation(final=True, next=["main"])
        def stop_v2(self):
            self.v2.off()
            return "main"
            
        @operation(final=True, next=["main"])
        def stop_v3(self):
            self.v3.off()
            return "main"            
    """

    shy = py2shy(app_v1_py)

    expected_shy = """App (v1: Valve, v2: Valve, v3: Valve) {
 main_1 -> stop_v1 {
  v1.on; 
 }
 main_2 -> stop_v2 {
  v2.on; 
 }
 main_3 -> stop_v3 {
  v3.on; 
 }
 initial main -> main_1, main_2, main_3 {}
 final stop_v1 -> main {
  v1.off; 
 }
 final stop_v2 -> main {
  v2.off; 
 }
 final stop_v3 -> main {
  v3.off; 
 }

}
""".strip()

    # print(shy)

    assert shy == expected_shy