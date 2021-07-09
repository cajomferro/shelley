WFORMED_UNDECLARED_START_EVENT = (
    "start_events must be included in events, got these extra"
)
WFORMED_UNDECLARED_TRIGGER_EVENT = (
    "All events must be defined in triggers. These triggers are undefined events"
)
WFORMED_UNDECLARED_TRIGGER_RULE = "The following trigger rules were not defined"

CHECK_TRACES_UNACCEPTED_VALID_TRACE = "Unaccepted valid trace"
CHECK_TRACES_UNEXPECTED_INVALID_TRACE = "Unexpected invalid trace"

MODEL_CHECK_UNDECLARED_EVENT_IN_TRACE = "Undeclared event in trace"
MODEL_CHECK_NO_INTERNAL_BEHAVIOR = (
    "Cannot call internal_model_checker if there is no internal behavior"
)

# TODO: AREN'T THESE WFORMED ERRORS TOO?
INTEGRATION_ERROR_ZERO_COMPONENTS = (
    "Should not be creating an internal behavior with 0 components"
)
SYSTEM_START_EVENT_REQUIRED = "At least one start event must be specified."  # this never occurs if we have a good parser? Wrong! Parser doesn't check for this.
SYSTEM_FINAL_EVENT_REQUIRED = "At least one final event must be specified."  # this never occurs if we have a good parser?
SYSTEM_START_STATE_KEYWORD_RESERVED = (
    lambda x: f"Start state '{x}' cannot have the same name as an event."
)
# SUC1: component with zero operations used
UNUSABLE_COMPONENT_TEXT = (
    lambda x: f"Subsystem {x} is declared but no operation is invoked."
)

# Invalid system
UNUSABLE_OPERATIONS_TEXT = "Unusable operation error"
# SUO1: unreachable operations
UNUSABLE_OPERATIONS_UNREACHABLE = lambda x: f"Unreachable operations: {', '.join(x)}"
# SUO2: operations that end in a sink state (point of no return). Is this equivalent to the concept of deadlock/progress?
# Deadlock better applies to concurrent systems which is not the case here. Progress captures best this notion.
UNUSABLE_OPERATIONS_NO_YIELD_POINT = (
    lambda x: f"These operations do not reach a yield point: {', '.join(x)}"
)

# Invalid integration
TRIGGER_NONE_SMALLEST_ERROR = (
    "dec_seq can only be none if failure is empty, which cannot be"
)
TRIGGER_NONE_INDEX = (
    "The index can only be None if the behavior is empty, which should never happen"
)
TRIGGER_UNEXPECTED_VALID_INTEGRATION = (
    lambda x: f"Expecting an invalid projection, but got: {x}"
)

INTEGRATION_ERROR_REPORT = (
    lambda macro, micro, micro_hl, err: f"""integration error

* system: {macro}
* integration: {micro}
               {micro_hl}
Instance errors:

{err}
"""
)

TRIGGER_INVALID_MICRO2MACRO = lambda seq: f"Sequence {seq} yields 0 derivations!"
AMBIGUITY_EXPECTED = f"Ambiguity expected"
UNDECLARED_OPERATION_IN_SUBSYSTEM = (
    lambda x, y: f"System operation '{x}' contains undeclared subsystem operations: {y}"
)
UNKNOWN_STATE = "Unknown state"
