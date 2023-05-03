from pathlib import Path
from shelley.parsers.shelley_lark_parser import parser as lark_parser, ShelleyLanguage
from shelley.shelley2automata import shelley2automata
from shelley.automata import (
    AssembledDevice,
    CheckedDevice,
)
from karakuri.regular import NFA
from shelley.shelleyc.serializer import _serialize_checked_device
import subprocess, sys

spec_controller: str = """Controller(
	a: Valve,
    b: Valve,
    t: Timer) {

    initial level1 -> standby1, level2 {
        a.on;
        t.begin;
    }

    level2 -> standby2 {
       t.end;
       b.on;
       t.begin;
    }

    final standby1 -> level1 {
        t.out;
        a.off;
    }

    final standby2 -> level1 {
        t.out;
        { a.off; b.off; }
		+
        {b.off; a.off; }
    }
}"""

spec_valve_a = """
base Valve {
  initial a_on -> a_off;
  final a_off -> a_on;
}
    """

spec_valve_b = """
base Valve {
  initial b_on -> b_off;
  final b_off -> b_on;
}
    """

spec_timer = """base Timer {
  initial t_begin -> t_end, t_out;
  final t_end -> t_begin;
  final t_out -> t_begin;
}"""


def empty_devices(name: str) -> CheckedDevice:
    raise ValueError()


def main():
    # Timer
    timer_automata = shelley2automata(
        ShelleyLanguage().transform(lark_parser.parse(spec_timer))
    )
    assembled_timer: AssembledDevice = AssembledDevice.make(
        timer_automata, empty_devices
    )

    # Valve a
    valve_a_automata = shelley2automata(
        ShelleyLanguage().transform(lark_parser.parse(spec_valve_a))
    )
    assembled_valve_a: AssembledDevice = AssembledDevice.make(
        valve_a_automata, empty_devices
    )

    # Valve a
    valve_b_automata = shelley2automata(
        ShelleyLanguage().transform(lark_parser.parse(spec_valve_b))
    )
    assembled_valve_b: AssembledDevice = AssembledDevice.make(
        valve_b_automata, empty_devices
    )

    shuffle = NFA.shuffle(assembled_timer.external.nfa, assembled_valve_a.external.nfa)
    shuffle = NFA.shuffle(shuffle, assembled_valve_b.external.nfa)

    shuffle_out = Path() / "shuffle.scy"

    _serialize_checked_device(shuffle_out, shuffle.as_dict())

    try:
        call = ["shelleyv", "--format", "png", "shuffle.scy", "-o", "shuffle.png", "-v"]
        subprocess.run(call, capture_output=True, check=True)
    except subprocess.CalledProcessError as err:
        print(err.output.decode() + err.stderr.decode())
        sys.exit(255)

    # shelleyv --format png shuffle.scy -o shuffle.png -v


if __name__ == "__main__":
    main()
