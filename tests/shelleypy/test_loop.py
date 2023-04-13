import pytest

from shelley.ast.visitors.shelley2lark import Shelley2Lark
from shelley.shelleypy.checker.exceptions import ShelleyPyError
from shelley.shelleypy.visitors.python_to_shelley import Python2ShelleyVisitor


def py2shy(py_code: str) -> str:
    device = Python2ShelleyVisitor(external_only=False).py2shy(py_code)

    shy2lark_visitor = Shelley2Lark(components=device.components)
    device.accept(shy2lark_visitor)

    return shy2lark_visitor.result.strip()


def test_while() -> None:
    """

    """

    app = """
    @claim("system check G (main -> F (main & END));")
    @system(uses={"v": "Valve"})
    class App:
        def __init__(self):
            self.v = Valve()

        @operation(initial=True, final=True, next=[])
        def main(self):
            i = 0
            while i < 10:
                self.v.on()
                wait(10)
                self.v.off()
                wait(10)
                i += 1
            return ""
    """

    shy = py2shy(app)

    expected_shy = """
App (v: Valve) {
 initial final main ->  {
  loop{v.on; v.off;} 
 }

}
""".strip()

    # print(shy)
    assert shy == expected_shy


def test_for() -> None:
    """

    """

    app = """
    @claim("system check G (main -> F (main & END));")
    @system(uses={"v": "Valve"})
    class App:
        def __init__(self):
            self.v = Valve()

        @operation(initial=True, final=True, next=[])
        def main(self):
            for _ in range(10):
                self.v.on()
                wait()
                self.v.off()
            return ""
    """

    shy = py2shy(app)

    expected_shy = """
App (v: Valve) {
 initial final main ->  {
  loop{v.on; v.off;} 
 }

}
""".strip()

    assert shy == expected_shy


def test_nested_for() -> None:
    """

    """

    app = """
    @system(uses={"v1": "Valve", "v2": "Valve"})
    class App:
        def __init__(self):
            self.v1 = Valve()
            self.v2 = Valve()

        @operation(initial=True, final=True, next=[])
        def main(self):
            for _ in range(10):
                self.v1.on()
                for _ in range(10):
                    self.v2.on()
                    wait(10)
                    self.v2.off()
                    wait(10)
                self.v1.off()
            return ""
    """

    shy = py2shy(app)

    expected_shy = """
App (v1: Valve, v2: Valve) {
 initial final main ->  {
  loop{v1.on; loop{v2.on; v2.off;} v1.off;} 
 }

}
""".strip()
    # print(shy)
    assert shy == expected_shy


def test_loop_with_return_v1() -> None:
    """

    """

    app = """
    @claim("system check G (main -> F (main & END));")
    @system(uses={"v": "Valve"})
    class App:
        def __init__(self):
            self.v = Valve()

        @operation(initial=True, final=True, next=[])
        def main(self):
            for i in range(10):
                return ""
    """

    with pytest.raises(ShelleyPyError) as exc_info:
        py2shy(app)

    assert str(exc_info.value.msg) == ShelleyPyError.ALL_BRANCH_RETURN_INSIDE_LOOP
    assert exc_info.value.lineno == 10


def test_loop_with_return_v2() -> None:
    """

    """

    app = """
    @claim("system check G (main -> F (main & END));")
    @system(uses={"v": "Valve"})
    class App:
        def __init__(self):
            self.v = Valve()

        @operation(initial=True, final=True, next=[])
        def main(self):
            for i in range(10):
                if i == 5:
                    self.v.on()
                    return ""
                else:
                    return ""
    """

    with pytest.raises(ShelleyPyError) as exc_info:
        py2shy(app)

    assert str(exc_info.value.msg) == ShelleyPyError.ALL_BRANCH_RETURN_INSIDE_LOOP
    assert exc_info.value.lineno == 10

def test_loop_with_return_v3() -> None:
    """

    """

    app = """
    @claim("system check G (main -> F (main & END));")
    @system(uses={"v1": "Valve", "v2": "Valve"})
    class App:
        def __init__(self):
            self.v1 = Valve()
            self.v2 = Valve()

        @operation(initial=True, final=True, next=[])
        def main(self):
            self.v2.on()
            for i in range(10):
                if (i % 2) == 0:
                    self.v1.on()
                    self.v1.off()
                    self.v2.off()
                    return ""
                else:
                    self.v2.off()
                    self.v2.on()
            self.v2.off()
            return ""
    """

    shy = py2shy(app)
    # print(shy)
    expected_shy = """
App (v1: Valve, v2: Valve) {
 final main_1 ->  {
  v2.on; loop{v2.off; v2.on;} v1.on; v1.off; v2.off; 
 }
 final main_2 ->  {
  v2.on; loop{v2.off; v2.on;} v2.off; 
 }
 initial main -> main_1, main_2 {}

}
    """.strip()
    assert shy == expected_shy


def test_loop_with_return_v4() -> None:
    """

    """

    app = """
    @claim("system check G (main -> F (main & END));")
    @system(uses={"v1": "Valve", "v2": "Valve"})
    class App:
        def __init__(self):
            self.v1 = Valve()
            self.v2 = Valve()

        @operation(initial=True, final=True, next=[])
        def main(self, handle_v1=True):
            self.v2.on()
            for i in range(10):
                if (i % 2) == 0:
                    if handle_v1: # extra branch here
                        self.v1.on()
                        self.v1.off()
                    self.v2.off()
                    return ""
                else:
                    self.v2.off()
                    self.v2.on()
            self.v2.off()                    
            return ""
    """

    shy = py2shy(app)
    print(shy)
    expected_shy = """
App (v1: Valve, v2: Valve) {
 final main_1 ->  {
  v2.on; loop{v2.off; v2.on;} {v1.on; v1.off;} + {} v2.off; 
 }
 final main_2 ->  {
  v2.on; loop{v2.off; v2.on;} v2.off; 
 }
 initial main -> main_1, main_2 {}

}
    """.strip()
    assert shy == expected_shy

def test_loop_with_return_v5() -> None:
    """

    """

    app = """
    @claim("system check G (main -> F (main & END));")
    @system(uses={"v1": "Valve", "v2": "Valve"})
    class App:
        def __init__(self):
            self.v1 = Valve()
            self.v2 = Valve()

        @operation(initial=True, final=True, next=[])
        def main(self, handle_v1=True):
            self.v2.on()
            for i in range(10):
                if (i % 2) == 0:
                    self.v1.on()
                    self.v1.off()
                    self.v2.off()
                else:
                    self.v2.off()
                    self.v2.on()
            self.v2.off()                    
            return "" # this is te only return
    """

    shy = py2shy(app)

    expected_shy = """App (v1: Valve, v2: Valve) {
 initial final main ->  {
  v2.on; loop{{v1.on; v1.off; v2.off;} + {v2.off; v2.on;}} v2.off; 
 }

}
    """.strip()
    print(shy)
    assert shy == expected_shy

def test_loop_with_return_v6() -> None:
    """

    """

    app = """
    @system(uses={"v1": "Valve"})
    class VHandler:
        def __init__(self):
            self.v1 = Valve()
    
        @operation(initial=True, next=["all_tries_failed", "close"])
        def main(self, allow_open=False):
            self.v1.vinit()
            for _ in range(10):
                match self.v1.test():
                    case "ok":
                        self.v1.ok()
                        if allow_open:
                            self.v1.open()
                        return "close"
                    case "error":
                        self.v1.error()
            self.v1.clean()
            return "all_tries_failed"
    
        @operation(final=True, next=[""])
        def all_tries_failed(self):
            return ""
    
    
        @operation(final=True, next=[""])
        def close(self):
            self.v1.close()
            return ""
    """

    shy = py2shy(app)
    print(shy)
    expected_shy = """
VHandler (v1: Valve) {
 main_1 -> close {
  v1.vinit; loop{v1.test; v1.error;} v1.test; v1.ok; {v1.open;} + {} 
 }
 main_2 -> all_tries_failed {
  v1.vinit; loop{v1.test; v1.error;} v1.clean; 
 }
 initial main -> main_1, main_2 {}
 final all_tries_failed ->  {}
 final close ->  {
  v1.close; 
 }

}
    """.strip()
    assert shy == expected_shy

def test_loop_nested_match_v1() -> None:
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
        for _ in range(10):
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
  loop{a.test; {a.clean; b.test; b.xalala; a.cenas;} + {a.omg;}} a.test; a.open; 
 }
 try_open_2 -> when_b {
  loop{a.test; {a.clean; b.test; b.xalala; a.cenas;} + {a.omg;}} a.test; a.clean; b.test; b.open; 
 }
 try_open_3 -> try_open {
  loop{a.test; {a.clean; b.test; b.xalala; a.cenas;} + {a.omg;}} a.test; a.clean; b.test; b.clean; 
 }
 try_open_4 -> try_open {
  loop{a.test; {a.clean; b.test; b.xalala; a.cenas;} + {a.omg;}} 
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
    # print(shy)
    assert shy == expected_shy

def test_loop_nested_match_v2() -> None:
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
        for _ in range(10):
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
                    return "try_open" # --> new return here
                case "omg":
                    self.a.omg() # this is the only XOR branch now
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
  loop{a.test; a.omg;} a.test; a.open; 
 }
 try_open_2 -> when_b {
  loop{a.test; a.omg;} a.test; a.clean; b.test; b.open; 
 }
 try_open_3 -> try_open {
  loop{a.test; a.omg;} a.test; a.clean; b.test; b.clean; 
 }
 try_open_4 -> try_open {
  loop{a.test; a.omg;} a.test; a.clean; b.test; b.xalala; a.cenas; 
 }
 try_open_5 -> try_open {
  loop{a.test; a.omg;} 
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
    # print(shy)
    assert shy == expected_shy

def test_loop_nested_match_all_branches_return() -> None:
    """
    If all branches return, the loop is useless
    """

    py_code = """
@system(uses={"a": "Valve", "b": "Valve"})
class App:
    def __init__(self):
        self.a = Valve()
        self.b = Valve()

    @operation(initial=True, next=["try_open", "when_a", "when_b"])
    def try_open(self):
        for _ in range(10):
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
                    return "try_open" # --> new return here
                case "omg":
                    self.a.omg() #
                    return "try_open" # --> new return here (all branches inside loop now return)
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

    with pytest.raises(ShelleyPyError) as exc_info:
        py2shy(py_code)

    assert str(exc_info.value.msg) == ShelleyPyError.ALL_BRANCH_RETURN_INSIDE_LOOP
    assert exc_info.value.lineno == 10


def test_if_before_match_loop_match() -> None:
    """
    """

    app_py = """
    @system(uses={"c": "Controller"})
    class App:
        def __init__(self):
            self.c = Controller()
    
        @op_initial_final
        def run(self, dry_run=False, max_tries=3):
            self.c.boot()
    
            if dry_run:
                match self.c.try_update():
                    case "follow_plan_online":
                        self.c.follow_plan_online()
                        self.c.sleep()  # Omit this for integration error
                        return ["run"]
                    case "follow_plan_offline":
                        self.c.follow_plan_offline()
                        self.c.sleep()
                        return ["run"]
                    case "try_update_error":
                        self.c.try_update_error()
    
                for _ in range(max_tries):
                    match self.c.try_update():
                        case "follow_plan_online":
                            self.c.follow_plan_online()
                            self.c.sleep()  # Omit this for integration error
                            return ["run"]
                        case "follow_plan_offline":
                            self.c.follow_plan_offline()
                            self.c.sleep()
                            return ["run"]
                        case "try_update_error":
                            self.c.try_update_error()
                else: # omit this for integration error
                    self.c.follow_plan_offline()
    
            self.c.sleep()
            return ["run"]
    """

    shy = py2shy(app_py)

    expected_shy = """App (c: Controller) {
 final run_1 -> run {
  c.boot; c.try_update; c.follow_plan_online; c.sleep; 
 }
 final run_2 -> run {
  c.boot; c.try_update; c.follow_plan_offline; c.sleep; 
 }
 final run_3 -> run {
  c.boot; c.try_update; c.try_update_error; loop{c.try_update; c.try_update_error;} c.try_update; c.follow_plan_online; c.sleep; 
 }
 final run_4 -> run {
  c.boot; c.try_update; c.try_update_error; loop{c.try_update; c.try_update_error;} c.try_update; c.follow_plan_offline; c.sleep; 
 }
 final run_5 -> run {
  c.boot; {c.try_update; c.try_update_error; c.try_update; c.try_update_error; loop{c.try_update; c.try_update_error;} c.follow_plan_offline;} + {} c.sleep; 
 }
 initial run -> run_1, run_2, run_3, run_4, run_5 {}

}
""".strip()

    # print(shy)

    assert shy == expected_shy