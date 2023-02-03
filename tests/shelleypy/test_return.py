import pytest

from shelley.ast.visitors.shelley2lark import Shelley2Lark
from shelley.shelleypy.checker.exceptions import ShelleyPyError, ReturnMatchesNext, NextOpsNotInReturn
from shelley.shelleypy.visitors.python_to_shelley import Python2ShelleyVisitor


def py2shy(py_code: str) -> str:
    device = Python2ShelleyVisitor(external_only=False).py2shy(py_code)

    shy2lark_visitor = Shelley2Lark(components=device.components)
    device.accept(shy2lark_visitor)

    return shy2lark_visitor.result.strip()


def test_missing_return_v1() -> None:
    """
    Missing a return an operation without branches/match/loop
    """

    app = """
    @system(uses={"v": "Valve"})
    class App:
        def __init__(self):
            self.v = Valve()

        @operation(initial=True, final=True, next=[])
        def main(self):
            self.v.run()
            # return "" --> this is missing!
    """

    with pytest.raises(ShelleyPyError) as exc_info:
        py2shy(app)

    assert str(exc_info.value.msg) == ShelleyPyError.MISSING_RETURN
    assert exc_info.value.lineno == 7


def test_missing_return_v2() -> None:
    """
    Missing a return an operation without branches/match/loop
    """

    app = """
    @system(uses={"v": "Valve"})
    class App:
        def __init__(self):
            self.v = Valve()

        @operation(initial=True, final=True, next=[])
        def main(self):
            pass
            # return "" --> this is missing!
    """

    with pytest.raises(ShelleyPyError) as exc_info:
        py2shy(app)

    assert str(exc_info.value.msg) == ShelleyPyError.MISSING_RETURN
    assert exc_info.value.lineno == 7

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

def test_missing_return_if() -> None:
    """
    Missing a return inside if or in the end of the function
    """

    app = """
    @system(uses={"v": "Valve"})
    class App:
        def __init__(self):
            self.v = Valve()

        @operation(initial=True, final=True, next=[])
        def main(self):
            if x:
                self.v.run()
                # return "" --> return is missing here...
            else:
                return ""  
            # ... or here
    """

    with pytest.raises(ShelleyPyError) as exc_info:
        py2shy(app)

    assert str(exc_info.value.msg) == ShelleyPyError.MISSING_RETURN
    assert exc_info.value.lineno == 7


# def test_missing_return_if_v2() -> None:
#     """
#     Missing a return inside if
#     """
#
#     app = """
#     @system(uses={"v": "Valve"})
#     class App:
#         def __init__(self):
#             self.v = Valve()
#
#         @operation(initial=True, final=True, next=[])
#         def main(self):
#             if x:
#                 self.v.run()
#             # return "" --> this is missing!
#     """
#
#     with pytest.raises(ShelleyPyError) as exc_info:
#         py2shy(app)
#
#     assert str(exc_info.value.msg) == ShelleyPyError.MISSING_RETURN
#     assert exc_info.value.lineno == 7


def test_return_ok_if_v2() -> None:
    app = """
    @system(uses={"v": "Valve"})
    class App:
        def __init__(self):
            self.v = Valve()

        @operation(initial=True, final=True, next=[])
        def main(self):
            if x:
                self.v.run()
                return "" # this is ok!
            else:
                return ""
    """

    shy = py2shy(app)

    expected_shy = """App (v: Valve) {
 final main_1 ->  {
  v.run; 
 }
 final main_2 ->  {}
 initial main -> main_1, main_2 {}

}
    """.strip()

    # print(shy)

    assert shy == expected_shy


def test_missing_return_else() -> None:
    """
    Missing a return inside else or in the end of the function
    """

    app = """
    @system(uses={"v": "Valve"})
    class App:
        def __init__(self):
            self.v = Valve()

        @operation(initial=True, final=True, next=[])
        def main(self):
            if x:
                self.v.run()
                return ""
            else:
                self.v.cancel()
                # return "" -->  return is missing here...
            # ... or here
    """

    with pytest.raises(ShelleyPyError) as exc_info:
        py2shy(app)

    assert str(exc_info.value.msg) == ShelleyPyError.MISSING_RETURN
    assert exc_info.value.lineno == 7


def test_missing_return_else_ok() -> None:
    """
    For now, if one branch has return the other has to have too!
    """

    app = """
    @system(uses={"v": "Valve"})
    class App:
        def __init__(self):
            self.v = Valve()

        @operation(initial=True, final=True, next=[])
        def main(self):
            if x:
                self.v.run()
                return ""
            else:
                self.v.cancel()
            return "" # this is ok!
    """

    shy = py2shy(app)

    expected_shy = """App (v: Valve) {
 final main_1 ->  {
  v.run; 
 }
 final main_2 ->  {
  v.cancel; 
 }
 initial main -> main_1, main_2 {}

}
        """.strip()

    # print(shy)

    assert shy == expected_shy


def test_return_does_not_match_next() -> None:
    """
    Testing that the value of the return matches what is annotated in the next=[...]
    """

    app = """
    @system(uses={"v": "Valve"})
    class App:
        def __init__(self):
            self.v = Valve()

        @operation(initial=True, final=True, next=["main"])
        def main(self):
            return "maixn" # this is a typo!
    """

    with pytest.raises(ReturnMatchesNext) as exc_info:
        py2shy(app)

    assert str(exc_info.value.msg) == "Return names ['maixn'] are not listed in the next operations!"
    assert exc_info.value.lineno == 9


def test_return_does_not_match_next_v2() -> None:
    """
    Testing that the value of the return matches what is annotated in the next=[...]
    """

    app = """
    @system(uses={"v": "Valve"})
    class App:
        def __init__(self):
            self.v = Valve()

        @operation(initial=True, final=True, next=[])
        def main(self):
            return "main"
    """

    with pytest.raises(ReturnMatchesNext) as exc_info:
        py2shy(app)

    assert str(exc_info.value.msg) == "Return names ['main'] are not listed in the next operations!"
    assert exc_info.value.lineno == 9


def test_return_does_not_match_next_v3() -> None:
    """
    All return values must coincide with the @next annotation
    """

    py_src = """
    @system(uses={"v1": "Valve"})
    class App:
        def __init__(self):
            self.v1 = Valve()

        @operation(initial=True, next=["stop"])
        def start(self):
            self.v1.on()
            return "stop"

        @operation(final=True, next=["stop"]) # ERROR HERE
        def stop(self):
            self.v1.on()                
            return "start" # AND HERE
    """

    with pytest.raises(ReturnMatchesNext) as exc_info:
        py2shy(py_src)

    assert str(exc_info.value.msg) == "Return names ['start'] are not listed in the next operations!"
    assert exc_info.value.lineno == 15

def test_next_against_return() -> None:
    """
    Every value in the @next annotation must be used in at least one return
    """

    py_src = """
    @system(uses={"v1": "Valve"})
    class App:
        def __init__(self):
            self.v1 = Valve()

        @operation(initial=True, next=["start", "stop"])
        def start(self):
            self.v1.on()
            return "stop"

        @operation(final=True, next=["start"]) # ERROR HERE
        def stop(self):
            self.v1.on()                
            return "start" # AND HERE
    """

    with pytest.raises(NextOpsNotInReturn) as exc_info:
        py2shy(py_src)

    assert str(exc_info.value.msg) == "Next operations {'start'} do not have a corresponding return!"
    assert exc_info.value.lineno == 7
