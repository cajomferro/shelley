import pytest

from shelley.ast.visitors.shelley2lark import Shelley2Lark
from shelley.shelleypy.checker.exceptions import ShelleyPyError
from shelley.shelleypy.visitors.python_to_shelley import Python2ShelleyVisitor


def py2shy(py_code: str) -> str:
    device = Python2ShelleyVisitor(external_only=False).py2shy(py_code)

    shy2lark_visitor = Shelley2Lark(components=device.components)
    device.accept(shy2lark_visitor)

    return shy2lark_visitor.result.strip()

def test_if_v1() -> None:
    """
    Simple return inside if and else
    """

    py_code = """
    @system(uses={"a": "Valve", "b": "Valve"})
    class App:
        def __init__(self):
            self.a = Valve()
            self.b = Valve()
    
        @operation(initial=True, final=True, next=["main"])
        def main(self, use_a=True):
            if use_a:
                self.a.on()
                self.a.off()
                return "main"
            else:
                self.b.on()
                self.b.off()
                return "main"
    """

    shy = py2shy(py_code)

    expected_shy = """App (a: Valve, b: Valve) {
 final main_1 -> main {
  a.on; a.off; 
 }
 final main_2 -> main {
  b.on; b.off; 
 }
 initial main -> main_1, main_2 {}

}
""".strip()

    assert shy == expected_shy


def test_if_v2() -> None:
    """
    """

    py_code = """
    @system(uses={"a": "Valve", "b": "Valve"})
    class App:
        def __init__(self):
            self.a = Valve()
            self.b = Valve()
    
        @operation(initial=True, next=["close_a", "close_b"])
        def open_all(self, use_a=True):
            if use_a:
                self.a.open()
            else:
                self.b.open()
                return "close_b"
    
            return "close_a"
        @operation(final=True, next=["open_all"])
        def close_a(self):
            self.a.close()
            return "open_all"
    
        @operation(final=True, next=["open_all"])
        def close_b(self):
            self.b.close()
            return "open_all"
    """

    shy = py2shy(py_code)

    expected_shy = """App (a: Valve, b: Valve) {
 open_all_1 -> close_b {
  b.open; 
 }
 open_all_2 -> close_a {
  a.open; 
 }
 initial open_all -> open_all_1, open_all_2 {}
 final close_a -> open_all {
  a.close; 
 }
 final close_b -> open_all {
  b.close; 
 }

}
""".strip()

    assert shy == expected_shy

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


def test_if_without_else_and_else_without_if() -> None:
    """
    Simple return inside if/else
    """

    py_code = """
    @system(uses={"v1": "Valve", "v2": "Valve"})
    class App:
        def __init__(self):
            self.v1 = Valve()
            self.v2 = Valve()
    
        @operation(initial=True, final=True, next=[])
        def main(self, handle_v1=True, val=0):
            self.v2.on()
            if (val % 2) == 0:
                if handle_v1:
                    self.v1.on()
                    self.v1.off()
                self.v2.off()
                return ""
            else:
                self.v2.off()
            return ""      
    """

    shy = py2shy(py_code)

    expected_shy = """App (v1: Valve, v2: Valve) {
 final main_1 ->  {
  v2.on; {v1.on; v1.off;} + {} v2.off; 
 }
 final main_2 ->  {
  v2.on; v2.off; 
 }
 initial main -> main_1, main_2 {}

}
""".strip()

    # print(shy)

    assert shy == expected_shy