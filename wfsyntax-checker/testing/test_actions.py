import unittest
from actions.checker import Action
from actions.checker import ActionsListDuplicatedError, ActionsListEmptyError
from actions.checker import check  # , check_actions_2, check_actions_3


class TestActions(unittest.TestCase):
    def test_is_valid(self):
        a_turn_on = Action('turnOn')
        a_turn_off = Action('turnOff')
        a_send = Action('send')
        actions_list = [a_turn_on, a_turn_off, a_send]  # type: List[Action]
        original_len = len(actions_list)

        s = check(actions_list)
        self.assertEqual(original_len, len(s))

    def test_is_empty(self):
        actions_list = []  # type: List[Action]

        with self.assertRaises(ActionsListEmptyError) as context:
            s = check(actions_list)

    def test_is_duplicated(self):
        a_turn_on = Action('turnOn')
        a_turn_on2 = Action('turnOn')
        a_turn_off = Action('turnOff')
        actions_list = [a_turn_on, a_turn_on2, a_turn_off]  # type: List[Action]

        with self.assertRaises(ActionsListDuplicatedError) as context:
            s = check(actions_list)


# class TestActions2(unittest.TestCase):
#     def test_is_valid(self):
#         aTurnOn = Action('turnOn')
#         aTurnOff = Action('turnOff')
#         aSend = Action('send')
#         actions_list = []  # type: List[Action]
#         actions_list.append(aTurnOn)
#         actions_list.append(aTurnOff)
#         actions_list.append(aSend)
#         original_len = len(actions_list)
#
#         s = set()
#         check_actions_2(actions_list, s)
#         self.assertEqual(original_len, len(s))
#
#     def test_is_empty(self):
#         actions_list = []  # type: List[Action]
#
#         with self.assertRaises(ActionsListEmptyError) as context:
#             check_actions_2(actions_list, set())
#
#     def test_is_duplicated(self):
#         aTurnOn = Action('turnOn')
#         aTurnOn2 = Action('turnOn')
#         aTurnOff = Action('turnOff')
#         actions_list = [aTurnOn, aTurnOn2, aTurnOff]  # type: List[Action]
#
#         with self.assertRaises(ActionsListDuplicatedError) as context:
#             check_actions_2(actions_list, set())


# class TestActions3(unittest.TestCase):
#     def test_is_valid(self):
#         aTurnOn = Action('turnOn')
#         aTurnOff = Action('turnOff')
#         aSend = Action('send')
#         actions_list = []  # type: List[Action]
#         actions_list.append(aTurnOn)
#         actions_list.append(aTurnOff)
#         actions_list.append(aSend)
#         original_len = len(actions_list)
#
#         s = check_actions_3(actions_list)
#         self.assertEqual(original_len, len(s))
#
#     def test_is_empty(self):
#         actions_list = []  # type: List[Action]
#
#         with self.assertRaises(ActionsListEmptyError) as context:
#             check_actions_3(actions_list)
#
#     def test_is_duplicated(self):
#         aTurnOn = Action('turnOn')
#         aTurnOn2 = Action('turnOn')
#         aTurnOff = Action('turnOff')
#         actions_list = [aTurnOn, aTurnOn2, aTurnOff]  # type: List[Action]
#
#         with self.assertRaises(ActionsListDuplicatedError) as context:
#             check_actions_3(actions_list)


if __name__ == '__main__':
    unittest.main()
