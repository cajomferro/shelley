import pytest

from shelley.ast.visitors.shelley2lark import Shelley2Lark
from shelley.shelleypy.checker.exceptions import ShelleyPyError
from shelley.shelleypy.checker.checker import extract_node
from shelley.shelleypy.visitors.python_to_shelley import Python2ShelleyVisitor
from shelley.shelleypy.visitors import VisitorHelper

def py2shy(py_code: str) -> str:
    visitor_helper = VisitorHelper(external_only=False)
    p2s_visitor = Python2ShelleyVisitor(visitor_helper)
    extract_node(py_code).accept(p2s_visitor)

    visitor = Shelley2Lark(components=visitor_helper.device.components)
    visitor_helper.device.accept(visitor)

    return visitor.result.strip()


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

def test_missing_return_if() -> None:
    """
    Missing a return inside if
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
                # return "" --> this is missing!
            else:
                return ""            
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

    #print(shy)

    assert shy == expected_shy


def test_missing_return_else() -> None:
    """
    Missing a return inside else
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
                # return "" --> this is missing!
    """

    with pytest.raises(ShelleyPyError) as exc_info:
        py2shy(app)

    assert str(exc_info.value.msg) == ShelleyPyError.IF_ELSE_MISSING_RETURN
    assert exc_info.value.lineno == 9


def test_missing_return_else_v2() -> None:
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
            return "" # For now we don't accept this because the else is still missing a return
    """

    with pytest.raises(ShelleyPyError) as exc_info:
        py2shy(app)

    assert str(exc_info.value.msg) == ShelleyPyError.IF_ELSE_MISSING_RETURN
    assert exc_info.value.lineno == 9


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

    with pytest.raises(ShelleyPyError) as exc_info:
        py2shy(app)

    assert str(exc_info.value.msg) == "Return names ['maixn'] do not match possible next operations ['main']!"
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

    with pytest.raises(ShelleyPyError) as exc_info:
        py2shy(app)

    assert str(exc_info.value.msg) == "Return names ['main'] do not match possible next operations []!"
    assert exc_info.value.lineno == 9