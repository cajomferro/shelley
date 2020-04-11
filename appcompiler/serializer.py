import logging
import pickle
import typing
import yaml
import os

from karakuri import regular

from .exceptions import CompilationError
from . import settings
from shelley.automata import CheckedDevice

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _test_extension_deserialize(path: str, binary=False):
    ext = os.path.splitext(path)[1].split(".")[1]
    if binary:
        expected = settings.EXT_SHELLEY_COMPILED_BIN
    else:
        expected = settings.EXT_SHELLEY_COMPILED_YAML
    if ext != expected:
        raise CompilationError('Invalid file: {2}. Expecting extension .{0} but found {1}!'.format(
            expected, ext, path))


# def _test_extension_serialize(path: str, binary=False):
#     ext = os.path.splitext(path)[1].split(".")[1]
#     if ext not in settings.EXT_SHELLEY_SOURCE_YAML:
#         raise CompilationError('Invalid file: {2}. Expecting extension .{0} but found {1}!'.format(
#             settings.EXT_SHELLEY_SOURCE_YAML, ext, path))


def _serialize_checked_device(path: str, device: CheckedDevice) -> typing.NoReturn:
    nfa_as_dict = device.nfa.as_dict(flatten=False)
    with open(path, 'w') as f:
        yaml.dump(nfa_as_dict, f)


def _deserialize_checked_device(path: str) -> CheckedDevice:
    with open(path, 'r') as f:
        yaml_load = yaml.load(f, Loader=yaml.FullLoader)
    nfa = regular.NFA.from_dict(yaml_load)
    return CheckedDevice(nfa)


def _serialize_checked_device_binary(path: str, device: CheckedDevice) -> typing.NoReturn:
    nfa_as_dict = device.nfa.as_dict(flatten=False)
    with open(path, 'wb') as f:
        pickle.dump(nfa_as_dict, f, pickle.HIGHEST_PROTOCOL)


def _deserialize_checked_device_binary(path: str) -> CheckedDevice:
    with open(path, 'rb') as f:
        load = pickle.load(f)
    nfa = regular.NFA.from_dict(load)
    return CheckedDevice(nfa)


def serialize(path: str, device: CheckedDevice, binary=False) -> typing.NoReturn:
    try:
        if binary:
            _serialize_checked_device_binary(path, device)
        else:
            _serialize_checked_device(path, device)
    except FileNotFoundError as error:
        raise error
    except Exception as error:
        if settings.VERBOSE:
            logger.exception(error)
        raise CompilationError("Invalid device!")


def deserialize(path: str, binary=False) -> CheckedDevice:
    _test_extension_deserialize(path, binary)
    try:
        if binary:
            device = _deserialize_checked_device_binary(path)
        else:
            device = _deserialize_checked_device(path)
    except FileNotFoundError as error:
        if settings.VERBOSE:
            logger.exception(error)
        raise CompilationError("Use device not found: {0}. Please compile it first!".format(path))
    except Exception as error:
        if settings.VERBOSE:
            logger.exception(error)
        raise CompilationError("Invalid device!")
    return device

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
