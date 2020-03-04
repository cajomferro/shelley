from typing import List, Set
from actions import Action


class ActionsListEmptyError(Exception):
    pass


class ActionsListDuplicatedError(Exception):
    pass


def check(actions_list: List[Action]) -> Set[Action]:
    _check(actions_list.copy())


def _check(actions_list: List[Action]) -> Set[Action]:
    """
    Get last element and do recursion on the rest
    :param actions_list:
    :return:
    """
    if len(actions_list) == 0:
        raise ActionsListEmptyError("List of actions cannot be empty!")

    # get element from tail
    a = actions_list.pop()  # type: Action

    if len(actions_list) == 0:
        return {a}
    else:
        result = _check(actions_list)  # type: Set[Action]
        if a in result:
            raise ActionsListDuplicatedError("Duplicated action: {0}".format(a.name))

        return result.union({a})

# def check_actions_2(actions_list: List[Action], s: Set[Action]) -> None:
#     """
#     This is an alternative but it is not as the specification
#     :param actions_list:
#     :param s:
#     :return:
#     """
#     if len(actions_list) == 0:
#         raise ActionsListEmptyError("List of actions cannot be empty!")
#
#     current_action = actions_list.pop()  # last a
#
#     for s_action in s:
#         if current_action.name == s_action.name:
#             raise ActionsListDuplicatedError("Duplicated action: {0}".format(current_action.name))
#     s.add(current_action)
#
#     if len(actions_list) > 0:
#         check_actions_2(actions_list, s)
#
#
# def check_actions_3(actions_list: List[Action]) -> Set[Action]:
#     """
#     Yet another alternative (difference on the base and recursive steps)
#     Get first element and do recursion on the rest
#     :param actions_list:
#     :return:
#     """
#     if len(actions_list) == 0:
#         raise ActionsListEmptyError("List of actions cannot be empty!")
#
#     if len(actions_list) == 1:
#         a = actions_list[0]
#         return {a}
#     else:
#         s_rest = check_actions_3(actions_list[1:])
#         s_cur = check_actions_3([actions_list[0]])
#
#         find_action = [action for action in s_rest if action.name == next(iter(s_cur)).name]
#
#         if len(find_action) > 0:
#             raise ActionsListDuplicatedError("Duplicated action: {0}".format(next(iter(s_cur)).name))
#         return s_cur.union(s_rest)
