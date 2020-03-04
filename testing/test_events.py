import unittest
from events.checker import GenericEvent, IEvent, EEvent, check, EventsListDuplicatedError, EventsListEmptyError


class TestEvents(unittest.TestCase):
    def test_is_valid(self):
        events = [IEvent('started'), IEvent('canceled'), EEvent('timeout')]  # type: List[GenericEvent]
        original_len = len(events)

        result_ievents, result_eevents = check(events)

        self.assertEqual(original_len, len(result_ievents) + len(result_eevents))

        self.assertEqual(2, len(result_ievents))
        self.assertEqual(1, len(result_eevents))

        self.assertTrue(IEvent('started') in result_ievents)
        self.assertFalse(IEvent('started') in result_eevents)

        self.assertTrue(IEvent('canceled') in result_ievents)
        self.assertFalse(IEvent('canceled') in result_eevents)

        self.assertFalse(IEvent('timeout') in result_ievents)
        self.assertTrue(IEvent('timeout') in result_eevents)

    def test_is_empty(self):
        with self.assertRaises(EventsListEmptyError) as context:
            check([])

    def test_is_duplicated_ievents(self):
        events = [IEvent('started'), IEvent('started')]  # type: List[GenericEvent]

        with self.assertRaises(EventsListDuplicatedError) as context:
            check(events)

    def test_is_duplicated_mixed_events(self):
        events = [IEvent('started'), EEvent('started')]  # type: List[GenericEvent]

        with self.assertRaises(EventsListDuplicatedError) as context:
            check(events)

    def test_is_duplicated_eevents(self):
        events = [EEvent('started'), EEvent('started')]  # type: List[GenericEvent]

        with self.assertRaises(EventsListDuplicatedError) as context:
            check(events)


# class TestEvents2(unittest.TestCase):
#     def test_is_valid(self):
#         events = [IEvent('started'), IEvent('canceled'), EEvent('timeout')]  # type: List[GenericEvent]
#         original_len = len(events)
#
#         result_ievents = []  # type(List[IEvent])
#         result_eevents = []  # type(List[EEvent]))
#         check_events2(events, result_ievents, result_eevents)
#         self.assertEqual(original_len, len(result_ievents) + len(result_eevents))
#         self.assertEqual(2, len(result_ievents))
#         self.assertEqual(1, len(result_eevents))
#
#         self.assertTrue(IEvent('started') in result_ievents)
#         self.assertFalse(IEvent('started') in result_eevents)
#
#         self.assertTrue(IEvent('canceled') in result_ievents)
#         self.assertFalse(IEvent('canceled') in result_eevents)
#
#         self.assertFalse(IEvent('timeout') in result_ievents)
#         self.assertTrue(IEvent('timeout') in result_eevents)
#
#     def test_is_empty(self):
#         with self.assertRaises(EventsListEmptyError) as context:
#             check_events2([], [], [])
#
#     def test_is_duplicated_ievents(self):
#         events = [IEvent('started'), IEvent('started')]  # type: List[GenericEvent]
#
#         with self.assertRaises(EventsListDuplicatedError) as context:
#             check_events2(events, [], [])
#
#     def test_is_duplicated_mixed_events(self):
#         events = [IEvent('started'), EEvent('started')]  # type: List[GenericEvent]
#
#         with self.assertRaises(EventsListDuplicatedError) as context:
#             check_events2(events, [], [])
#
#     def test_is_duplicated_eevents(self):
#         events = [EEvent('started'), EEvent('started')]  # type: List[GenericEvent]
#
#         with self.assertRaises(EventsListDuplicatedError) as context:
#             check_events2(events, [], [])

if __name__ == '__main__':
    unittest.main()
