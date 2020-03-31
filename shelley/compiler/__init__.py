import pickle
import typing

from karakuri import regular
from shelley.automata import CheckedDevice


def _serialize_checked_device(path: str, device: CheckedDevice) -> typing.NoReturn:
    with open(path, 'wb') as f:
        pickle.dump(device.nfa.as_dict(), f, pickle.HIGHEST_PROTOCOL)


def _deserialize_checked_device(path: str) -> CheckedDevice:
    with open(path, 'rb') as f:
        nfa = regular.NFA.from_dict(pickle.load(f))

    return CheckedDevice(nfa)
