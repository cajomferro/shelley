from pathlib import Path
import yaml
from typing import Any
import argparse
import shelley.shelleyv.main as shelleyv
from karakuri import regular
import io

EXAMPLES_PATH = Path() / Path(__file__).parent / "input"

CONTROLLER_INTEGRATION_MODEL = """
accepted_states:
- 3
- 4
edges:
- char: level1
  dst: 1
  src: 0
- char: level2
  dst: 2
  src: 1
- char: standby1
  dst: 3
  src: 1
- char: level1
  dst: 1
  src: 3
- char: standby2
  dst: 4
  src: 2
- char: level1
  dst: 1
  src: 4
start_state: 0
"""
EXPECTED_NUSMV_MODEL = """MODULE main
VAR
    _eos: boolean;
    _action: {level1, level2, standby1, standby2};
    _state: {0, 1, 2, 3, 4, 5};
ASSIGN
    init(_state) := {0};
    next(_state) := case
        _eos: _state; -- finished, no change in state
        _state=0 & _action=standby2: 1;
        _state=0 & _action=level2: 1;
        _state=0 & _action=standby1: 1;
        _state=0 & _action=level1: 2;
        _state=2 & _action=standby2: 1;
        _state=2 & _action=level1: 1;
        _state=2 & _action=level2: 3;
        _state=2 & _action=standby1: 4;
        _state=1 & _action=standby2: 1;
        _state=1 & _action=level2: 1;
        _state=1 & _action=standby1: 1;
        _state=1 & _action=level1: 1;
        _state=4 & _action=standby2: 1;
        _state=4 & _action=level2: 1;
        _state=4 & _action=standby1: 1;
        _state=4 & _action=level1: 2;
        _state=3 & _action=standby2: 5;
        _state=3 & _action=level2: 1;
        _state=3 & _action=standby1: 1;
        _state=3 & _action=level1: 1;
        _state=5 & _action=standby2: 1;
        _state=5 & _action=level2: 1;
        _state=5 & _action=standby1: 1;
        _state=5 & _action=level1: 2;
    esac;
    init(_action) := {level1, level2, standby1, standby2};
    next(_action) := case
        _eos : _action;
        TRUE : {level1, level2, standby1, standby2};
    esac;
    init(_eos) := {FALSE};
    next(_eos) := case
        _eos : TRUE;
        _state=2 & _action=standby1 : {TRUE, FALSE};
        _state=3 & _action=standby2 : {TRUE, FALSE};
        TRUE : FALSE;
    esac;
FAIRNESS _eos;
LTLSPEC F(_eos); -- sanity check
LTLSPEC  G(_eos -> G(_eos) & X(_eos)); -- sanity check
"""


def get_args():
    """
    This simulates a command line call with the --dfa command only
    (other parser arguments are required by the handle_fsm method but not included)
    @return:
    """
    parser = argparse.ArgumentParser()

    # 1. add required arguments to parser
    parser.add_argument("--dfa", action="store_true", help="Convert to a DFA first")
    parser.add_argument(
        "--no-epsilon", action="store_true", help="Remove epsilon transitions"
    )
    parser.add_argument(
        "--filter",
        default=None,
        help="Keep only the (operations/calls) that match the given regex, hide (epsilon) the remaining ones.",
    )
    parser.add_argument("--no-sink", action="store_true", help="Remove sink states")
    parser.add_argument("--minimize", action="store_true", help="Minimize the DFA")

    # 2. simulate a command with the --dfa option activated (the others are ignored)
    return parser.parse_args(["--dfa"])


def test_create_nusmv_model():
    fsm_dict = yaml.load(CONTROLLER_INTEGRATION_MODEL, Loader=yaml.FullLoader)
    n: regular.NFA[Any, str] = shelleyv.handle_fsm(
        regular.NFA.from_dict(fsm_dict), get_args()
    )

    file = io.StringIO()
    shelleyv.smv_dump(
        state_diagram=n.as_dict(flatten=True), fp=file,
    )

    smv = file.getvalue()
    # print(f"NuSMV model: {smv}")

    # TODO: how to guarantee that both strings are equal?
    assert (len(smv) - len(EXPECTED_NUSMV_MODEL)) == 0


#
# def test_dfa2spec() -> None:
#     input_path: Path = EXAMPLES_PATH / "subsystems.yml"
#
#     parent_system, subsystems = parse_input(input_path)
#
#     # print(parent_system)
#     # print(subsystems)
#     specs = generate_specs(subsystems)
#     expected_specs = [
#         "shelleyv timer.scy -f ltl --dfa -o t.out output --prefix t",
#         "shelleyv valve.scy -f ltl --dfa -o a.out output --prefix a",
#         "shelleyv valve.scy -f ltl --dfa -o b.out output --prefix b",
#     ]
#     assert specs == expected_specs


# def test_modelcheck() -> None:
#     uses_path: Path = EXAMPLES_PATH / "uses.yml"
#     system_path: Path = EXAMPLES_PATH / "controller.shy"
#
#     shelleymc_call = [
#         "shelleymc",
#         "-u",
#         str(uses_path),
#         "-s",
#         str(system_path),
#         "--integration-check",
#         "-v"
#     ]
#     print(" ".join(shelleymc_call))
#     checks = subprocess.check_output(shelleymc_call).decode("utf-8")
#     print(checks)
