import logging
from shelley.parsers.shelley_lark_parser import parse
import sys
import yaml
import argparse
import subprocess
from pathlib import Path
from typing import List, Mapping
from io import StringIO
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
    try:
        shelleyc.compile_shelley(
            src_path=spec, uses_path=uses, integration=integration, skip_checks=True,
        )
        logger.debug("OK!")
    except shelleyc.CompilationError as error:
        if VERBOSE:
            logger.error(str(error), exc_info=VERBOSE)
        else:
            print(str(error), file=sys.stderr)
        logger.debug("ERROR!")
        sys.exit(255)

    assert integration.exists()


def create_nusmv_model(integration: Path, output: Path, formula: List[str]) -> None:
    """
    Create NuSMV model file from integration file
    @param integration: path to integration file (FSM)
    @param output: path to NuSMV model (*.smv)
    @param formula: optional
    """

    logger.info(f"Creating NuSMV model: {output} | formula: {formula}")

    model: StringIO = shelleyv.create_smv_from_integration_model(integration)
    with output.open("w") as fp:
        fp.write(model.getvalue())

    if len(formula) > 0:
        logger.info("Appending LTL formula:", " & ".join(formula))

        ltl_call = [
            "ltl",
            "formula",
        ]
        checks = subprocess.check_output(ltl_call + formula)
        logger.debug(" ".join(ltl_call))
        logger.debug("LTL output: ", checks)
        with output.open("a+") as fp:
            fp.write(checks.decode("utf-8"))


def create_split_usage_model(
    system_spec: Path, integration: Path, subsystems: Mapping[str, Path]
) -> None:
    for (instance_name, instance_spec) in subsystems.items():
        # Create the integration SMV file
        usage_model_path = (
            system_spec.parent / f"{system_spec.stem}-{instance_name}.smv"
        )

        logger.debug("Creating", usage_model_path)
        model: StringIO = shelleyv.create_smv_from_integration_model(
            integration=integration, filter=instance_name + ".*"
        )
        with usage_model_path.open("w") as fp:
            fp.write(model.getvalue())

        ltl_call = [
            "ltl",
            "instance",
            "--spec",
            str(instance_spec),
            "--name",
            instance_name,
        ]
        checks = subprocess.check_output(ltl_call)
        logger.debug(" ".join(ltl_call))

        logger.debug("Model checking usage of", instance_name)
        with usage_model_path.open("a+") as fp:
            fp.write(checks.decode("utf-8"))
        try:
            subprocess.check_call(
                ["NuSMV", str(usage_model_path),]
            )
        except subprocess.CalledProcessError:
            sys.exit(255)


def generate_subsystems_integration_checks(
    nusmv_integration_model: Path, subsystems: Mapping[str, Path]
) -> None:
    with nusmv_integration_model.open("a+") as fp:
        for (instance_name, instance_spec) in subsystems.items():
            logger.info(f"Append LTL usage of {instance_name}")
            specs = ltlf.generate_spec(instance_spec, instance_name)

            for spec in specs:
                logger.debug(spec)
                fp.write(f"{str(spec)}\n")


def model_check_integration(nusmv_integration_model: Path) -> None:
    logger.info("Model checking integration...")
    try:
        nusmv_call = [
            "NuSMV",
            str(nusmv_integration_model),
        ]
        logger.debug(" ".join(nusmv_call))
        subprocess.check_call(nusmv_call)
    except subprocess.CalledProcessError:
        sys.exit(255)


def main():
    args = parse_command()

    if args.verbosity:
        VERBOSE = True
        logger.setLevel(logging.DEBUG)

    logger.debug(f"Current path: {Path.cwd()}")

    subsystems: Mapping[str, Path] = dict(get_instances(args.spec, args.uses))
    spec: Path = args.spec
    integration: Path = spec.parent / (spec.stem + "-i.scy")
    nusmv_integration_model: Path = spec.parent / f"{spec.stem}.smv"
    uses: Path = args.uses

    create_integration_model(spec, uses, integration)

    if (
        args.integration_check and not args.split_usage
    ) or not args.skip_integration_model:
        logger.debug("Split usage is disabled")
        create_nusmv_model(integration, nusmv_integration_model, args.formula)

    if args.integration_check:
        if args.split_usage:
            create_split_usage_model(spec, integration, subsystems)
        else:
            generate_subsystems_integration_checks(nusmv_integration_model, subsystems)

    if not args.skip_mc:
        model_check_integration(nusmv_integration_model)
