import dill
import typing

from shelley.automata import CheckedDevice


def _serialize_checked_device(path: str, device: CheckedDevice) -> typing.NoReturn:
    with open(path, 'wb') as f:
        dill.dump(device, f, dill.HIGHEST_PROTOCOL)


def _deserialize_checked_device(path: str) -> CheckedDevice:
    with open(path, 'rb') as f:
        device = dill.load(f)
    return device
