from pathlib import Path
from shelley.shelleyv import shelleyv
from shelley.parsers.ltlf_lark_parser import *

WORKDIR_PATH = Path() / Path(__file__).parent / "workdir"

EXPECTED_NUSMV_MODEL = """MODULE main
VAR
    _eos: boolean;
    _action: {level1, level2, standby1, standby2};
    _state: {0, 1, 2, 3, 4, 5};
ASSIGN
    init(_state) := {0};
    next(_state) := case
        _eos: _state; -- finished, no change in state
        _state=0 & _action=level2: 1;
        _state=0 & _action=standby2: 1;
        _state=0 & _action=standby1: 1;
        _state=0 & _action=level1: 2;
        _state=2 & _action=level2: 3;
        _state=2 & _action=standby2: 1;
        _state=2 & _action=level1: 1;
        _state=2 & _action=standby1: 4;
        _state=1 & _action=level2: 1;
        _state=1 & _action=standby2: 1;
        _state=1 & _action=standby1: 1;
        _state=1 & _action=level1: 1;
        _state=4 & _action=level2: 1;
        _state=4 & _action=standby2: 1;
        _state=4 & _action=standby1: 1;
        _state=4 & _action=level1: 2;
        _state=3 & _action=level2: 1;
        _state=3 & _action=standby1: 1;
        _state=3 & _action=level1: 1;
        _state=3 & _action=standby2: 5;
        _state=5 & _action=level2: 1;
        _state=5 & _action=standby2: 1;
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

LTLSPEC F (_eos); -- sanity check
LTLSPEC G (_eos -> G(_eos) & X(_eos)); -- sanity check
"""


def test_create_nusmv_model():
    integration_model_path = WORKDIR_PATH / "controller.scy"
    smv_path = WORKDIR_PATH / "controller.smv"
    shelleyv.fsm2smv(integration_model_path, smv_path)

    # TODO: how to guarantee that both strings are equal?
    with smv_path.open() as fp:
        # print(fp.read())
        assert (len(fp.read()) - len(EXPECTED_NUSMV_MODEL)) == 0

    smv_path.unlink()

def test_reify_ctl1():
    name = 'a'
    formula = CTL(LTL_F(Action(name=name, prefix=None)))
    EOS = Variable("eos")
    ACT = Variable("_action")
    given = ltlf_to_ltl(formula, eos=EOS, action=ACT)
    expected_a = And(Equal(ACT, Variable(name)), Not(EOS))
    assert given == expected_a

def test_reify_ctl2():
    formula = CTL(LTL_F(EndOfSequence()))
    EOS = Variable("eos")
    ACT = Variable("_action")
    given = ltlf_to_ltl(formula, eos=EOS, action=ACT)
    assert given == EOS

def test_reify_ctl3():
    name = 'a'
    formula = CTL(Or(LTL_F(Action(name=name, prefix=None)), LTL_F(EOS)))
    eos = Variable("eos")
    act = Variable("_action")
    given = ltlf_to_ltl(formula, eos=eos, action=act)
    expected_a = Or(And(Equal(act, Variable(name)), Not(eos)), eos)
    assert given == expected_a

def test_ctl_reify():
    name = 'start_http_ok'
    a = LTL_F(Action(name=name, prefix=None))
    eos = LTL_F(EndOfSequence())
    formula = CTL(ExistsFinally(And(a, ExistsFinally(eos))))
    EOS = Variable("eos")
    ACT = Variable("_action")
    #import pdb; pdb.set_trace()
    given = ltlf_to_ltl(formula, eos=EOS, action=ACT)
    expected_a = And(Equal(ACT, Variable(name)), Not(EOS))
    assert given == ExistsFinally(And(expected_a, ExistsFinally(EOS)))
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
