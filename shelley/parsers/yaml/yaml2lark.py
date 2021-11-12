from __future__ import annotations

from pathlib import Path
from shelley.parsers.yaml import yaml2shelley

from shelley.ast.visitors.shelley2lark import Shelley2Lark

def translate(yaml_source: Path, lark_source: Path):
    shelley_device = yaml2shelley.get_shelley_from_yaml(yaml_source)
    visitor = Shelley2Lark(components=shelley_device.components)
    shelley_device.accept(visitor)

    lark_code = visitor.result.strip()
    # print(lark_code)

    with lark_source.open("w") as f:
        f.write(lark_code)


def main():
    import sys

    if len(sys.argv) < 2:
        print("Please provide a valid source path! Usage: yaml2lark PATH")
        sys.exit(255)

    yaml_path = Path(sys.argv[1])
    lark_path = Path(sys.argv[1][:-4] + ".shy")
    # print(yaml_path)
    # print(lark_path)
    translate(yaml_path, lark_path)


if __name__ == "__main__":
    main()
