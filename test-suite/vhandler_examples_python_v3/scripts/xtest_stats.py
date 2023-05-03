import yaml, sys
from pathlib import Path
from karakuri import regular
from shelley.shelleyv import shelleyv


path: Path = Path(sys.argv[1])
with path.open() as fp:
    dict_nfa = yaml.load(fp, Loader=yaml.FullLoader)

n: regular.NFA = regular.NFA.from_dict(dict_nfa)

fsm_stats: shelleyv.FSMStats = shelleyv.handle_fsm(
    n=n,
    dfa=True,
    dfa_no_empty_string=False,
    dfa_minimize=False,
    nfa_no_sink=True,
    no_epsilon=False,
)

print(fsm_stats)
