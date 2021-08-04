WFORMED_UNDECLARED_OPERATION_RIGHT_SIDE = (
    lambda e1, e2: f"Operation {e2} on the right side of {e1} is never declared!"
)
WFORMED_NON_FINAL_LEFT_OPERATION_WITHOUT_RIGHT_SIDE = (
    lambda e1: f"Unusable operation {e1}. Hint: Mark {e1} as final or declare operations on the right side."
)
# TODO: implement this in LARK parser
# WFORMED_OPERATION_EMPTY_BODY = (
#     lambda e1: f"Operation {e1} is empty. Hint: Declare operations of subsystems in this operation."
# )
