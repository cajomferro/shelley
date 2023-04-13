import pytest

from shelley.ast.visitors.shelley2lark import Shelley2Lark
from shelley.shelleypy.checker.exceptions import ShelleyPyError, ReturnMatchesNext, NextOpsNotInReturn
from shelley.shelleypy.visitors.python_to_shelley import Python2ShelleyVisitor


def py2shy(py_code: str) -> str:
    device = Python2ShelleyVisitor(external_only=False).py2shy(py_code)

    shy2lark_visitor = Shelley2Lark(components=device.components)
    device.accept(shy2lark_visitor)

    return shy2lark_visitor.result.strip()

# TODO: move to test_return.py after fixed
def test_unreachable_code_v1() -> None:
    """
    TODO: this test is not passing since both of the cases return, hence
    it's not supposed that there is anything running after the match
    how to detect this?
    """

    app = """
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
            self.v1.cenas() # ERROR UNREACHABLE CODE FOR SHELLEYPY

        @operation(final=True, next=[""])
        def error(self):
            self.v1.clean()
            return ""


        @operation(final=True, next=[""])
        def close(self):
            self.v1.off()
            return ""
    """

    with pytest.raises(ShelleyPyError) as exc_info:
        py2shy(app)

    assert str(exc_info.value.msg) == ShelleyPyError.MISSING_RETURN
    assert exc_info.value.lineno == 7

# TODO: move to test_return.py after fixed
def test_unreachable_code_v2() -> None:
    """
    TODO: this test is not passing since both of the cases return, hence
    it's not supposed that there is anything running after the match
    how to detect this?
    """

    app = """
    @system(uses={"v1": "Valve"})
    class App:
        def __init__(self):
            self.v1 = Valve()

        @operation(initial=True, final=True, next=[])
        def main(self):
            match self.v1.test():
                case "open":
                    self.v1.open()
                    self.v1.close()
                    return ""
                case "clean":
                    self.v1.clean()
                    return ""
            self.v1.open() # THIS SHOULD BE UNREACHABLE
            self.v1.close()
            return ""
    """

    with pytest.raises(ShelleyPyError) as exc_info:
        py2shy(app)

    assert str(exc_info.value.msg) == ShelleyPyError.MISSING_RETURN
    assert exc_info.value.lineno == 7

# TODO: move to test_match.py after fixed
def test_nested_match_v5() -> None:
    """
    TODO: fix this scenario where all cases inside the match have return
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
                    case "open":
                        self.b.open()
                        return "when_b"
                    case "clean":
                        self.b.clean()
                        return "try_open"
            case "omg":
                self.a.omg()
        self.a.last()
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
  # a.test; {a.clean; b.test;} + {a.omg;} a.last; # --> FIX! THIS IS WRONG!
  a.test; a.omg; a.last; # --> SHOULD BE THIS INSTEAD
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

# TODO: move to test_match.py after fixed
def test_match_after_match_with_match_inside() -> None:
    """
    # TODO: this is a bug in the checker. Fix this scenario.
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
                case "error":
                    self.v2.error()

            match self.v1.test():
                case "ok":
                    self.v1.ok()
                    match self.v1.test():
                        case "ok":
                            self.v1.ok()
                        case "error":
                            self.v2.error()                    
                case "error":
                    self.v2.error()

            return ""
    """

    shy = py2shy(app_py)

    expected_shy = """App (v1: Valve, v2: Valve) {
 initial main ->  {
  v1.test; {v1.ok;} + {v2.error;} v1.test; {v1.ok; v1.test; {v1.ok;} + {v2.error;} } + {v2.error;} 
 }

}
""".strip()

    # print(shy)

    assert shy == expected_shy

# TODO: This is a variation of test_loop.py.test_if_before_match_loop_match
# See shelley-examples/bad_coordination_2023_paper_aquamote_example
# it is based on the coordination aquamote use case (artefact)
# this does not compile with Shelley because the generate Shelley is wrong
# but I don't even know right now what should be the correct generated version
def test_if_before_match_loop_match() -> None:
    """
    # TODO: this is a bug in the checker. Fix this scenario.
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
                self.c.sleep()
    
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
  c.boot; {c.sleep;} + {} + {c.try_update_error;} c.try_update; c.follow_plan_online; c.sleep; 
 }
 final run_2 -> run {
  c.boot; {c.sleep;} + {} + {c.try_update_error;} c.try_update; c.follow_plan_offline; c.sleep; 
 }
 final run_3 -> run {
  c.boot; {c.sleep;} + {} + {c.try_update_error;} c.try_update; {c.sleep;} + {} + {c.try_update_error;} loop{c.try_update; c.try_update_error;} c.try_update; c.follow_plan_online; c.sleep; 
 }
 final run_4 -> run {
  c.boot; {c.sleep;} + {} + {c.try_update_error;} c.try_update; {c.sleep;} + {} + {c.try_update_error;} loop{c.try_update; c.try_update_error;} c.try_update; c.follow_plan_offline; c.sleep; 
 }
 final run_5 -> run {
  c.boot; {c.sleep;} + {} + {c.try_update_error;} c.try_update; {c.sleep;} + {} + {c.try_update_error;} c.try_update; c.try_update_error; loop{c.try_update; c.try_update_error;} c.follow_plan_offline; c.sleep; 
 }
 initial run -> run_1, run_2, run_3, run_4, run_5 {}

}
""".strip()

    # print(shy)

    assert shy == expected_shy