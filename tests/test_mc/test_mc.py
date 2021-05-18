from pathlib import Path
from shelley.modelchecker.dfa2spec import parse_input, generate_specs

EXAMPLES_PATH = Path() / "tests" / "test_mc" / "input"


def test1() -> None:
    input_path: Path = EXAMPLES_PATH / "subsystems.yml"

    parent_system, subsystems = parse_input(input_path)

    # print(parent_system)
    # print(subsystems)

    print(generate_specs(subsystems))

