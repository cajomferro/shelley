import unittest
from behaviours.checker import *
from behaviours import *


class TestBehaviours(unittest.TestCase):
    def test_is_valid(self):
        ebegin = EEvent('begin')
        astop = Action('stop')
        elevel1 = EEvent('level1')
        elevel2 = EEvent('level2')
        estdby = EEvent('standby')
        ebye = IEvent('bye')

        e_events = [elevel1, elevel2, estdby]  # type: List[EEvent]
        i_events = [ebye]  # type: List[IEvent]

        actions = [astop]

        behaviours = [Behaviour(ebegin, elevel1),
                      Behaviour(elevel1, estdby),
                      Behaviour(elevel1, elevel2),
                      Behaviour(elevel2, estdby),
                      Behaviour(estdby, elevel1),
                      Behaviour(estdby, ebye, astop)
                      ]
        original_len = len(behaviours)

        result = []  # type(List[Tuple[GenericEvent, GenericEvent]]))

        check(behaviours, actions, i_events, e_events, result)

        self.assertEqual(original_len, len(result))

        self.assertTrue(behaviours[0] in result)
        self.assertTrue(behaviours[1] in result)
        self.assertTrue(behaviours[2] in result)
        self.assertTrue(behaviours[3] in result)
        self.assertTrue(behaviours[4] in result)
        self.assertTrue(behaviours[5] in result)

        self.assertFalse(Behaviour(ebegin, ebye, Action("")) in result)

    def test_behaviours_left_ievent_ok(self):
        """
        Internal events on left do not need action
        :return:
        """
        ebegin = EEvent('begin')
        ex = EEvent('x')
        ey = IEvent('y')

        e_events = [ex]  # type: List[EEvent]
        i_events = [ey]  # type: List[IEvent]

        action = Action("a")
        actions = [action]

        behaviours = [Behaviour(ebegin, ex),
                      Behaviour(ey, ex)  # TESTING HERE
                      ]

        original_len = len(behaviours)

        result = []  # type(List[Tuple[GenericEvent, GenericEvent]]))

        check(behaviours, actions, i_events, e_events, result)

        self.assertEqual(original_len, len(result))

    def test_behaviour_missing_begin(self):
        ex = EEvent('x')
        ey = EEvent('y')

        e_events = [ex, ey]  # type: List[EEvent]
        i_events = []  # type: List[IEvent]

        actions = []

        behaviours = [Behaviour(ex, ey),
                      Behaviour(ey, ex)
                      ]

        result = []  # type(List[Tuple[GenericEvent, GenericEvent]]))

        with self.assertRaises(BehavioursMissingBegin) as context:
            check(behaviours, actions, i_events, e_events, result)

    def test_behaviour_missing_action(self):
        with self.assertRaises(BehaviourMissingActionForInternalEvent) as context:
            Behaviour(GenericEvent('x'), IEvent('y'))

    def test_behaviour_unexpected_action(self):
        with self.assertRaises(BehaviourUnexpectedActionForExternalEvent) as context:
            Behaviour(GenericEvent('x'), EEvent('y'), Action('a'))

    def test_empty_behaviours(self):
        with self.assertRaises(BehavioursListEmptyError) as context:
            check([], [], [], [], [])

    def test_left_event_undeclared(self):
        eleft = EEvent('left')
        eright = EEvent('right')

        e_events = [eright]  # type: List[EEvent]
        i_events = []  # type: List[IEvent]

        actions = []

        behaviours = [Behaviour(eleft, eright)]

        result = []  # type(List[Tuple[GenericEvent, GenericEvent]]))

        with self.assertRaises(BehaviourEventUndeclared) as context:
            check(behaviours, actions, i_events, e_events, result)

        self.assertEqual(str(context.exception), "Left event must be declared either as internal or external event")

    def test_right_external_event_undeclared(self):
        eleft = EEvent('left')
        eright = EEvent('eright')

        e_events = [eleft]  # type: List[EEvent]
        i_events = []  # type: List[IEvent]

        actions = []

        behaviours = [Behaviour(eleft, eright)]

        result = []  # type(List[Tuple[GenericEvent, GenericEvent]]))

        with self.assertRaises(BehaviourEventUndeclared) as context:
            check(behaviours, actions, i_events, e_events, result)

        self.assertEqual(str(context.exception), "Right external event 'eright' was not declared")

    def test_action_internal_event_undeclared(self):
        eleft = EEvent('left')
        iright = IEvent('iright')

        e_events = [eleft]  # type: List[EEvent]
        i_events = [iright]  # type: List[IEvent]

        action = Action("a")
        actions = []

        behaviours = [Behaviour(eleft, iright, action)]

        result = []  # type(List[Tuple[GenericEvent, GenericEvent]]))

        with self.assertRaises(BehaviourActionForInternalEventUndeclared) as context:
            check(behaviours, actions, i_events, e_events, result)

        self.assertEqual(str(context.exception), "Action 'a' not declared for internal event 'iright'")

    def test_right_internal_event_undeclared(self):
        eleft = EEvent('left')
        iright = IEvent('iright')

        e_events = [eleft]  # type: List[EEvent]
        i_events = []  # type: List[IEvent]

        action = Action("a")
        actions = [action]

        behaviours = [Behaviour(eleft, iright, action)]

        result = []  # type(List[Tuple[GenericEvent, GenericEvent]]))

        with self.assertRaises(BehaviourEventUndeclared) as context:
            check(behaviours, actions, i_events, e_events, result)

        self.assertEqual(str(context.exception), "Right internal event 'iright' was not declared")

    def test_behaviours_duplicated(self):
        ebegin = EEvent('begin')
        ex = EEvent('x')
        ey = EEvent('y')

        e_events = [ex, ey]  # type: List[EEvent]
        i_events = []  # type: List[IEvent]

        actions = []

        behaviours = [Behaviour(ebegin, ex),
                      Behaviour(ex, ey),
                      Behaviour(ex, ey),  # dup
                      Behaviour(ey, ex),
                      ]

        result = []  # type(List[Tuple[GenericEvent, GenericEvent]]))

        with self.assertRaises(BehavioursListDuplicatedError) as context:
            check(behaviours, actions, i_events, e_events, result)

        self.assertEqual(str(context.exception), "Duplicated behaviour: x -> y")

    def test_behaviours_duplicated_right_ievent(self):
        ebegin = EEvent('begin')
        ex = EEvent('x')
        ey = IEvent('y')

        e_events = [ex]  # type: List[EEvent]
        i_events = [ey]  # type: List[IEvent]

        action = Action("a")
        actions = [action]

        behaviours = [Behaviour(ebegin, ex),
                      Behaviour(ex, ey, action),
                      Behaviour(ex, ey, action),  # dup
                      Behaviour(ey, ex),
                      ]

        result = []  # type(List[Tuple[GenericEvent, GenericEvent]]))

        with self.assertRaises(BehavioursListDuplicatedError) as context:
            check(behaviours, actions, i_events, e_events, result)

        self.assertEqual(str(context.exception), "Duplicated behaviour: x -> y")


if __name__ == '__main__':
    unittest.main()
