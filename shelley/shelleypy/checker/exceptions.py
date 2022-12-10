# README: moved here because of module cyclic dependencies problems

class ShelleyPyError(Exception):
    MISSING_RETURN = "Missing return!"
    CASE_MISSING_RETURN = "Missing return for case!"
    IF_ELSE_MISSING_RETURN = "One of the if/else branches has return and the other not!"
    ELSE_MISSING = "The else branch is missing!"
    MATCH_CALL_TYPE = "Match call type mismatch. Accepted types are: Call, Await!"
    MATCH_CASE_VALUE_TYPE = "Cases values must be strings!"
    RETURN_PARSE_ERROR = "Could not parse return. Expecting str|list[,*]"
    DECORATOR_PARSE_ERROR = "Could not parse decorator!"

    def __init__(self, lineno: int, msg: str):
        self.lineno = lineno
        self.msg = msg
        super().__init__(self.msg)


class CompilationError(Exception):
    pass
