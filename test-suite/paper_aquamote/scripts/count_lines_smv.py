import os
from pathlib import Path
import subprocess, sys
from typing import List, Dict, Tuple
import numpy as np
import pandas as pd


def find_groups_and_targets(path: Path) -> Tuple[List[str], List[Path]]:
    """
    Groups contains a filtered list of devices (e.g., controller, valve, etc.)
    Targets contains a filtered list of paths that have the .smv extension 
    """
    groups: List[str] = []
    targets: List[Path] = []

    for filename in sorted(os.listdir(path)):
        filepath: Path = Path(filename)
        basename: str = filepath.stem
        if filepath.is_file() and filepath.suffix == ".smv":
            targets.append(filepath)
            groupname = basename.split("-")[0]
            if groupname not in groups:
                groups.append(groupname)
    # print(groups)
    # print(targets)

    return groups, targets


def count_lines(path: Path) -> int:
    # https://stackoverflow.com/questions/114814/count-non-blank-lines-of-code-in-bash
    # https://unix.stackexchange.com/questions/11305/show-all-the-file-up-to-the-match
    # exclude comments and blank lines
    cmd = f"cat {path} | sed '/^\s*#/d;/^\s*--/d;/^\s*$/d;' | wc -l"
    ps = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    output = ps.communicate()[0]
    loc = int(output.strip())

    return loc


def get_totals(data: pd.DataFrame, group: str) -> Tuple[int, int]:
    # find all values from column "loc" whose column "group" belong to current group and sum them
    totals_loc = data.loc[data["group"] == group, "loc"].sum()

    i_loc = data.loc[
        (data["name"].str.contains("-d") | data["name"].str.contains("-i")) & (data["group"] == group), "loc"
    ].sum()

    # print(i_loc)
    totals_without_i = totals_loc - i_loc

    return totals_loc, totals_without_i


def add_row(data: pd.DataFrame, group: str, name: str, loc: int) -> pd.DataFrame:
    row = pd.DataFrame.from_records([{"group": group, "name": name, "loc": loc}])
    data = data.append(row, ignore_index=True)

    return data


def main():
    path = Path()

    groups, targets = find_groups_and_targets(path)

    data = pd.DataFrame()
    for group in groups:
        for target in targets:
            target_basename = target.stem.split("-")[0]
            if target_basename == group:
                data = add_row(data, group, target.stem, count_lines(target))

        totals_loc, totals_without_i = get_totals(data, group)

        data = add_row(data, group, f"totals", totals_loc)

        data = add_row(data, group, f"totals*", totals_without_i)

    print(data)
    print("TOTALS")
    print(data.loc[data["name"].str.contains("\*")])

    print("SUM")
    print(data.loc[data["name"].str.contains("\*")].sum())

    # print(data.loc[data["name"].str.contains("totals*")])


if __name__ == "__main__":
    main()
