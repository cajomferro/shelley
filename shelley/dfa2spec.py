import yaml
from typing import Dict, Tuple
from pathlib import Path


def parse_input(input_path: Path) -> Tuple[str, Dict[str, str]]:
    input_dict: Dict[str, Dict[str, str]]
    with input_path.open(mode="r") as f:
        input_dict = yaml.safe_load(f)

    parent_system: str = input_dict["parent"]
    subsystems: Dict[str, str] = input_dict["subsystems"]

    return parent_system, subsystems


def dfa2spec(prefix, input_path, output_path):
    print(f"shelleyv {input_path} -f ltl --dfa -o {output_path} output --prefix {prefix}")


def generate_specs(subsystems):
    for prefix, path in subsystems.items():
        dfa2spec(prefix, path, f"{prefix}.out")


def main():
    pass  # see example under tests


if __name__ == "__main__":
    main()
