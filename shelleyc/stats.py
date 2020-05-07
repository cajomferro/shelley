import json
from typing import IO
from dataclasses import asdict

from shelley.automata import AssembledDevice


def save_timings(fp: IO[str], device: AssembledDevice) -> None:
    # Print out the timings
    # The keys of the dictionary are timedelta objects, which we must
    # convert to strings so that humans can understand what they are
    timings = asdict(device.get_timings())
    for k in timings:
        # convert timedelta to strings
        timings[k] = str(timings[k])
    json.dump(timings, fp)


def save_statistics(fp: IO[str], device: AssembledDevice) -> None:
    # Print out stats (may take a long time)
    json.dump(asdict(device.get_stats()), fp)
