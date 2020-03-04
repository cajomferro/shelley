from events import GenericEvent, IEvent, EEvent
from actions import Action


class BehaviourMissingActionForInternalEvent(Exception):
    pass


class BehaviourUnexpectedActionForExternalEvent(Exception):
    pass


class Behaviour:
    e1 = None
    e2 = None
    action = None

    def __init__(self, e1: GenericEvent, e2: GenericEvent, action: Action = None):
        self.e1 = e1
        self.e2 = e2
        self.action = action
        if isinstance(self.e2, IEvent) and self.action is None:
            raise BehaviourMissingActionForInternalEvent("Behaviour with internal event must specify an action")
        if isinstance(self.e2, EEvent) and self.action is not None:
            raise BehaviourUnexpectedActionForExternalEvent("Behaviour with external event does not require an action")

    def __eq__(self, other):
        if not isinstance(other, Behaviour):
            # don't attempt to compare against unrelated types
            raise Exception("Instance is not of Behaviour type")

        return self.e1.name == other.e1.name and self.e2.name == other.e2.name
