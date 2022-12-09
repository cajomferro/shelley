class ShelleyPyError(Exception):
    LIST_CASE = "Cases with lists are not supported!"
    MISSING_RETURN = "Missing return!"
    CASE_MISSING_RETURN = "Missing return for case!"
    IF_ELSE_MISSING_RETURN = "One of the if/else branches has return and the other not!"
    MATCH_CALL_TYPE = "Match call type mismatch. Accepted types are: Call, Await!"

    def __init__(self, lineno: int, msg: str):
        self.lineno = lineno
        self.msg = msg
        super().__init__(self.msg)
