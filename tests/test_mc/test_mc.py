from pathlib import Path
from shelley.shelleymc.dfa2spec import parse_input, generate_specs

EXAMPLES_PATH = Path() / "tests" / "test_mc" / "input"


def test1() -> None:
    input_path: Path = EXAMPLES_PATH / "subsystems.yml"

    parent_system, subsystems = parse_input(input_path)

    # print(parent_system)
    # print(subsystems)
    specs = generate_specs(subsystems)
    expected_specs = [
        "shelleyv timer.scy -f ltl --dfa -o t.out output --prefix t",
        "shelleyv valve.scy -f ltl --dfa -o a.out output --prefix a",
        "shelleyv valve.scy -f ltl --dfa -o b.out output --prefix b",
    ]
    assert specs == expected_specs
