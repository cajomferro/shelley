# README: moved here because of module cyclic dependencies problems
from typing import List, Set


class ShelleyPyError(Exception):
    DUPLICATED_METHOD = "Duplicated method!"
    MISSING_RETURN = "Missing return!"
    CASE_MISSING_RETURN = "Missing return for case!"
    MATCH_CALL_TYPE = "Match call type mismatch. Accepted types are: Call, Await!"
    MATCH_CASE_VALUE_TYPE = "Cases values must be strings!"
    RETURN_PARSE_ERROR = "Could not parse return. Expecting str|list[,*]"
    ALL_BRANCH_RETURN_INSIDE_LOOP = "All branches return which makes loop useless. Please remove the loop."

    # DECORATOR_PARSE_ERROR = "Could not parse decorator!"

    def __init__(self, lineno: int, msg: str):
        self.lineno = lineno
        self.msg = msg
        super().__init__(self.msg)


class ReturnMatchesNext(ShelleyPyError):
    def __init__(self, lineno: int, return_name: List[str]):
        self.lineno = lineno
        super().__init__(
            lineno, f"Return names {return_name} are not listed in the next operations!"
        )


class NextOpsNotInReturn(ShelleyPyError):
    def __init__(self, lineno: int, missing_returns: Set[str]):
        self.lineno = lineno
        super().__init__(
            lineno,
            f"Next operations {missing_returns} do not have a corresponding return!",
        )


class CompilationError(Exception):
    pass
