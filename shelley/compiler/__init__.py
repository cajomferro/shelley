import dill
import typing
import yaml
import os

from karakuri import regular
from shelley.automata import CheckedDevice


def serialize_checked_device(path: str, device: CheckedDevice) -> typing.NoReturn:
    with open(path, 'w') as f:
        yaml.dump(device.nfa.as_dict(), f)


def deserialize_checked_device(path: str) -> CheckedDevice:
    with open(path, 'r') as f:
        nfa = regular.NFA.from_dict(yaml.load(f, Loader=yaml.BaseLoader))

    return CheckedDevice(nfa)


def serialize_checked_device_binary(path: str, device: CheckedDevice) -> typing.NoReturn:
    with open(path, 'wb') as f:
        dill.dump(device, f, dill.HIGHEST_PROTOCOL)


def deserialize_checked_device_binary(path: str) -> CheckedDevice:
    with open(path, 'rb') as f:
        return dill.load(f)

# def _serialize_checked_device_with_yaml(path: str, device: CheckedDevice) -> typing.NoReturn:
#     with open(path, 'w') as f:
#         yaml.dump(device.nfa.as_dict(), f)
#
#
# def _serialize_checked_device_with_pickle(path: str, device: CheckedDevice) -> typing.NoReturn:
#     with open(path, 'wb') as f:
#         pickle.dump(device.nfa.as_dict(), f, pickle.HIGHEST_PROTOCOL)
#
#
# def _deserialize_checked_device_with_yaml(path: str) -> CheckedDevice:
#     with open(path, 'r') as f:
#         nfa = regular.NFA.from_dict(yaml.load(f, Loader=yaml.BaseLoader))
#
#     return CheckedDevice(nfa)
#
#
# def _deserialize_checked_device_with_pickle(path: str) -> CheckedDevice:
#     with open(path, 'rb') as f:
#         nfa = regular.NFA.from_dict(pickle.load(f))
#
#     return CheckedDevice(nfa)
#
#
# def _serialize_checked_device(target_dir: str, target_name: str, device: CheckedDevice, binary=False) -> str:
#     """
#
#     :param target_dir:
#     :param target_name:
#     :param device:
#     :param binary:
#     :return: path to generated file
#     """
#     if binary:
#         path = os.path.join(target_dir, '{0}.shelcb'.format(target_name))
#         _serialize_checked_device_with_pickle(path, device)
#     else:
#         path = os.path.join(target_dir, '{0}.shelc.yaml'.format(target_name))
#         _serialize_checked_device_with_yaml(path, device)
#     return path
#
#
# def _deserialize_checked_device(path: str, binary=False) -> CheckedDevice:
#     """
#
#     :param target_dir:
#     :param target_name:
#     :param device:
#     :param binary:
#     :return: path to generated file
#     """
#
#     if binary:
#         device = _deserialize_checked_device_with_pickle(path)
#     else:
#         device = _deserialize_checked_device_with_yaml(path)
#     return device
