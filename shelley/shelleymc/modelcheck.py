import logging
from shelley.parsers.shelley_lark_parser import parse
import sys
import yaml
import argparse
import subprocess
from pathlib import Path
from typing import List, Mapping, Optional
from shelley.shelleyc import shelleyc
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


def create_fsm_models(spec: Path, uses: Path, fsm_integration: Path) -> Path:
    """
    Create integration model by running shelleyc tool
    input: system spec + uses
    output: integration (FSM) (*-i.scy)
    """

    logger.info(f"Creating integration model: {fsm_integration}")

    try:
        fsm_system: Path = shelleyc.compile_shelley(
            src_path=spec,
            uses_path=uses,
            integration=fsm_integration,
            dump_timings=sys.stdout,
            skip_checks=True,
        )
    except shelleyc.CompilationError as err:
        if VERBOSE:
            logger.exception(err, exc_info=True)
        logger.error(err)
        sys.exit(255)

    assert fsm_system.exists()
    assert fsm_integration.exists()

    return fsm_system


def create_nusmv_model(
    integration: Path, smv: Path, ltlf_formulae: Optional[List[str]] = None
) -> None:
    """
    Create NuSMV model file from integration file
    @param integration: path to integration file (FSM)
    @param smv: path to NuSMV model (*.smv)
    @param ltlf_formulae: optional
    """

    logger.info(f"Creating NuSMV model: {smv} | formula: {ltlf_formulae}")
    shelleyv.fsm2smv(integration, smv)

    if ltlf_formulae is not None and len(ltlf_formulae) > 0:
        logger.info("Appending LTL formulae:", " & ".join(ltlf_formulae))
        ltl_formulae: List[str] = ltlf.convert_ltlf_formulae(ltlf_formulae)
        for ltl in ltl_formulae:
            logger.debug(f"LTL output: {ltl}")
            with smv.open("a+") as fp:
                fp.write(f"{ltl}\n")


def append_ltl_usage(instance_spec: Path, instance_name: str, smv_path: Path):
    logger.info(f"Append LTL usage of {instance_name} ({instance_spec})")

    specs = ltlf.generate_instance_spec(instance_spec, instance_name)
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
        shelleyv.fsm2smv(
            fsm_model=integration,
            smv_model=smv_path,
            filter_instance=instance_name + ".*",
        )

        append_ltl_usage(instance_spec, instance_name, smv_path)

        logger.debug("Model checking usage of", instance_name)
        model_check(smv_path)


def check_nusmv_output(raw_output: str):
    lines_output: List[str] = raw_output.splitlines()
    # print(lines_output)

    # filter_output = [line for line in lines_output if line.startswith("-- specification")]
    for line in lines_output:
        print(line)

    for line in lines_output:
        if line.startswith("-- specification") and "is false" in line:
            sys.exit(255)


def model_check(smv_path: Path) -> None:
    try:
        nusmv_call = [
            "NuSMV",
            str(smv_path),
        ]
        logger.debug(" ".join(nusmv_call))
        cp: subprocess.CompletedProcess = subprocess.run(
            nusmv_call, capture_output=True, check=True
        )
        check_nusmv_output(cp.stdout.decode())
    except subprocess.CalledProcessError:
        logger.exception("NuSMV error!")
        sys.exit(255)


def main():
    global VERBOSE
    args = parse_command()

    if args.verbosity:
        VERBOSE = True
        logger.setLevel(logging.DEBUG)

    logger.debug(f"Current path: {Path.cwd()}")

    subsystems: Mapping[str, Path] = dict(get_instances(args.spec, args.uses))
    spec: Path = args.spec
    fsm_integration: Path = spec.parent / (spec.stem + "-i.scy")
    smv_system: Path = spec.parent / f"{spec.stem}.smv"
    smv_integration: Path = spec.parent / f"{spec.stem}-i.smv"
    uses: Path = args.uses

    fsm_system: Path = create_fsm_models(spec, uses, fsm_integration)
    create_nusmv_model(fsm_system, smv_system)
    ltl_system_spec: str = ltlf.generate_system_spec(spec)
    # with smv_system.open("a+") as fp:
    #     fp.write(f"{ltl_system_spec}\n")

    if not args.skip_mc:
        logger.info("Model checking system...")
        model_check(smv_system)

    if (
        args.integration_check and not args.split_usage
    ) or not args.skip_integration_model:
        logger.debug("Split usage is disabled")
        create_nusmv_model(fsm_integration, smv_integration, args.formula)

    if args.integration_check:
        if args.split_usage:
            create_split_usage_model(spec, fsm_integration, subsystems)
        else:
            for (instance_name, instance_spec) in subsystems.items():
                append_ltl_usage(instance_spec, instance_name, smv_integration)

    if not args.skip_mc:
        logger.info("Model checking integration...")
        model_check(smv_integration)
