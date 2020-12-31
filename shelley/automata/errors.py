WFORMED_UNDECLARED_START_EVENT = "start_events must be included in events, got these extra"
WFORMED_UNDECLARED_TRIGGER_EVENT = "All events must be defined in triggers. These triggers are undefined events"
WFORMED_UNDECLARED_TRIGGER_RULE = "The following trigger rules were not defined"

CHECK_TRACES_UNACCEPTED_VALID_TRACE = "Unaccepted valid trace"
CHECK_TRACES_UNEXPECTED_INVALID_TRACE = "Unexpected invalid trace"

MODEL_CHECK_UNDECLARED_EVENT_IN_TRACE = "Undeclared event in trace"
MODEL_CHECK_NO_INTERNAL_BEHAVIOR = "Cannot call internal_model_checker if there is no internal behavior"

# TODO: AREN'T THESE WFORMED ERRORS TOO?
INTEGRATION_ERROR_ZERO_COMPONENTS = "Should not be creating an internal behavior with 0 components"
DEVICE_ERROR_START_EVENT_REQUIRED = "At least one start event must be specified."
DEVICE_ERROR_FINAL_EVENT_REQUIRED = "At least one final event must be specified."
DEVICE_ERROR_START_STATE_KEYWORD_RESERVED = lambda x: f"Start state '{x}' cannot have the same name as an event."
UNUSABLE_COMPONENT_TEXT = "Component is declared but no operation is invoked."

UNUSABLE_OPERATIONS_TEXT = "Unusable operation error"
UNUSABLE_OPERATIONS_UNREACHABLE = lambda x: f"Unreachable operations: {', '.join(x)}"
UNUSABLE_OPERATIONS_YIELD_POINT = lambda x: f"These operations do not reach a yield point: {', '.join(x)}"

TRIGGER_INTEGRATION_SMALLEST_ERROR = "dec_seq can only be none if failure is empty, which cannot be"
TRIGGER_INTEGRATION_NONE_INDEX = "The index can only be None if the behavior is empty, which should never happen"
TRIGGER_INTEGRATION_UNEXPECTED_VALID_INTEGRATION = lambda x: f"Expecting an invalid projection, but got: {x}"
TRIGGER_INTEGRATION_REPORT = lambda macro, micro, micro_hl, \
                                    err: f"integration error\n\n{macro}\n{micro}\n{micro_hl}\nInstance errors:\n\n{err}"

TRIGGER_INTEGRATION_INVALID_MICRO2MACRO = lambda seq: f"Sequence {seq} yields 0 derivations!"

AMBIGUITY_EXPECTED = f"Ambiguity expected"

INTEGRATION_UNDECLARED_OPERATION_IN_SUBSYSTEM = lambda x, y: f"System operation '{x}' contains undeclared subsystem operations: {y}"
INTEGRATION_UNKNOWN_STATE = "Unknown state"