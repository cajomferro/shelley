import logging
from shelley.parsers.shelley_lark_parser import parse
import sys
import yaml
import argparse
import subprocess
from pathlib import Path
from typing import List, Mapping
from shelley import shelleyc
from shelley.shelleyv import shelleyv
from shelley.shelleymc import ltlf

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("shelleymc")
VERBOSE: bool = False


def get_instances(dev_path: Path, uses_path: Path):
    if uses_path is None:
        uses_path = dict()
    with uses_path.open() as f:
        uses = yaml.safe_load(f)
    dev = parse(dev_path)
    for (k, v) in dev.components:
        filename = Path(uses[v])
        yield (k, filename.parent / f"{filename.stem}.shy")


def parse_command():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--spec", "-s", type=Path, help="Shelley specification.", required=True
    )
    parser.add_argument("--uses", "-u", type=Path, help="The uses YAML file.")
    parser.add_argument(
        "--formula", "-f", nargs="*", help="Give a correctness claim", default=[]
    )
    parser.add_argument("--integration-check", action="store_true")
    parser.add_argument("--skip-mc", action="store_true")
    parser.add_argument(
        "--split-usage",
        action="store_true",
        help="Check the usage of each subsystem separately.",
    )
    parser.add_argument("--skip-integration-model", action="store_true")
    parser.add_argument(
        "-v", "--verbosity", help="increase output verbosity", action="store_true"
    )

    return parser.parse_args()


def create_integration_model(spec: Path, uses: Path, integration: Path) -> None:
    """
    Create integration model by running shelleyc tool
    input: system spec + uses
    output: integration (FSM) (*-i.scy)
    """

    logger.info(f"Creating integration model: {integration}")

    shelleyc.compile_shelley(
        src_path=spec, uses_path=uses, integration=integration, skip_checks=True,
    )

    assert integration.exists()


def create_nusmv_model(integration: Path, smv: Path, ltlf_formulae: List[str]) -> None:
    """
    Create NuSMV model file from integration file
    @param integration: path to integration file (FSM)
    @param smv: path to NuSMV model (*.smv)
    @param ltlf_formulae: optional
    """

    logger.info(f"Creating NuSMV model: {smv} | formula: {ltlf_formulae}")
    shelleyv.create_smv_from_integration_model(integration, smv)

    if len(ltlf_formulae) > 0:
        logger.info("Appending LTL formulae:", " & ".join(ltlf_formulae))
        ltl_formulae: List[str] = ltlf.convert_ltlf_formulae(ltlf_formulae)
        for ltl in ltl_formulae:
            logger.debug(f"LTL output: {ltl}")
            with smv.open("a+") as fp:
                fp.write(f"{ltl}\n")


def append_ltl_usage(instance_spec: Path, instance_name: str, smv_path: Path):
    logger.info(f"Append LTL usage of {instance_name}")
    specs = ltlf.generate_spec(instance_spec, instance_name)
    for spec in specs:
        logger.debug(spec)
        with smv_path.open("a+") as fp:
            fp.write(f"{spec}\n")


def create_split_usage_model(
    system_spec: Path, integration: Path, subsystems: Mapping[str, Path]
) -> None:
    for (instance_name, instance_spec) in subsystems.items():
        # Create the integration SMV file
        smv_path = system_spec.parent / f"{system_spec.stem}-{instance_name}.smv"

        logger.debug("Creating", smv_path)
        shelleyv.create_smv_from_integration_model(
            integration=integration, smv_path=smv_path, filter=instance_name + ".*"
        )

        append_ltl_usage(instance_spec, instance_name, smv_path)

        logger.debug("Model checking usage of", instance_name)
        model_check_integration(smv_path)


def model_check_integration(smv_path: Path) -> None:
    logger.info("Model checking integration...")
    try:
        nusmv_call = [
            "NuSMV",
            str(smv_path),
        ]
        logger.debug(" ".join(nusmv_call))
        subprocess.check_call(nusmv_call)
    except subprocess.CalledProcessError:
        sys.exit(255)


def main():
    global VERBOSE
    args = parse_command()

    if args.verbosity:
        VERBOSE = True
        logger.setLevel(logging.DEBUG)

    logger.debug(f"Current path: {Path.cwd()}")

    subsystems: Mapping[str, Path] = dict(get_instances(args.spec, args.uses))
    spec_path: Path = args.spec
    integration_path: Path = spec_path.parent / (spec_path.stem + "-i.scy")
    smv_path: Path = spec_path.parent / f"{spec_path.stem}.smv"
    uses_path: Path = args.uses

    create_integration_model(spec_path, uses_path, integration_path)

    if (
        args.integration_check and not args.split_usage
    ) or not args.skip_integration_model:
        logger.debug("Split usage is disabled")
        create_nusmv_model(integration_path, smv_path, args.formula)

    if args.integration_check:
        if args.split_usage:
            create_split_usage_model(spec_path, integration_path, subsystems)
        else:
            for (instance_name, instance_spec) in subsystems.items():
                append_ltl_usage(instance_spec, instance_name, smv_path)

    if not args.skip_mc:
        model_check_integration(smv_path)
