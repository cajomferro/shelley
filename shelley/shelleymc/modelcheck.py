import logging
from typing import Tuple
from shelley.parsers import shelley_lark_parser
import sys
import yaml
import argparse
import subprocess
from pathlib import Path
from typing import List, Mapping, Optional
from shelley.shelleyc import shelleyc
from shelley.ast.devices import Device
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
    dev = shelley_lark_parser.parse(dev_path)
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
    parser.add_argument("--skip-mc", action="store_true")
    parser.add_argument("--skip-direct", action="store_true")
    parser.add_argument(
        "--split-usage",
        action="store_true",
        help="Check the usage of each subsystem separately.",
    )
    parser.add_argument(
        "-v", "--verbosity", help="increase output verbosity", action="store_true"
    )

    return parser.parse_args()


def create_fsm_system_model(
    spec: Path, uses: Path, fsm_system: Path, skip_direct_checks: bool = False,
) -> Tuple[Device, shelleyc.AssembledDevice]:
    """
    Create integration model by running shelleyc tool
    input: system spec + uses
    output: integration (FSM) (*-i.scy)
    """
    if VERBOSE and not skip_direct_checks:
        dump_timings = sys.stdout
        shelleyc.settings.VERBOSE = True
    else:
        dump_timings = None

    try:
        device, assembled_device = shelleyc.compile_shelley(
            src_path=spec,
            dst_path=fsm_system,
            uses_path=uses,
            dump_timings=dump_timings,
            skip_checks=skip_direct_checks,
        )
    except shelleyc.CompilationError as err:
        if VERBOSE:
            logger.error(err, exc_info=True)
        else:
            logger.error(err)
        sys.exit(255)

    assert fsm_system.exists()
    logger.debug(f"Created FSM system model")
    if assembled_device.internal is not None:
        logger.debug(f"Created FSM integration model")

    return device, assembled_device


# def create_nusmv_model(fsm: Path, smv: Path) -> None:
#     """
#     Create NuSMV model file from integration file
#     @param integration: path to integration file (FSM)
#     @param smv: path to NuSMV model (*.smv)
#     @param ltlf_formulae: optional
#     """
#
#     shelleyv.fsm2smv(fsm, smv)


def create_system_model(dev: Device, fsm: Path, smv: Path):
    logger.debug(f"Creating NuSMV system model: {smv}")
    shelleyv.fsm2smv(fsm, smv)

    logger.debug(f"Generating system specs: {fsm}")
    ltl_system_specs: List[str] = ltlf.generate_system_spec(dev)

    # TODO: do we want LTLf formulae from command line for system spec?
    dump_ltl_specs(ltl_system_specs, smv)


def append_ltl_from_command_line(formula: List[str], smv_path: Path) -> None:
    """
    Check if there are LTLF formulae from the command line to be parsed.
    Translate LTLf to LTL formulae (as a list of strings)
    @param formula: list of LTLf formulae
    @return:
    """

    if formula is not None and len(formula) > 0:
        logger.debug(
            "Appending LTL formula from cmd line: {0}".format(" & ".join(formula))
        )
        ltlf_formulae: List[ltlf.Formula] = ltlf.parse_ltlf_formulae(formula)
        ltl_formulae: List[str] = ltlf.convert_ltlf_formulae(ltlf_formulae)

        dump_ltl_specs(ltl_formulae, smv_path, "CMD LINE SPECS")


def dump_ltl_specs(specs: List[str], smv_path: Path, comment_line: str = None):
    with smv_path.open("a+") as fp:
        if comment_line is not None:
            fp.write(f"\n--{comment_line}\n")
        for spec in specs:
            logger.debug(spec)
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

        specs = ltlf.generate_instance_spec(instance_spec, instance_name)
        dump_ltl_specs(specs, smv_path)

        logger.debug("Model checking usage of", instance_name)
        model_check(smv_path)


def create_instance_model(
    fsm: Path, smv: Path, subsystems: Mapping[str, Path], cmd_line_specs: List[str]
):
    shelleyv.fsm2smv(fsm, smv)

    for (instance_name, instance_spec) in subsystems.items():
        dev: Device = shelley_lark_parser.parse(instance_spec)
        specs = ltlf.generate_instance_spec(dev, instance_name)
        dump_ltl_specs(specs, smv)

    append_ltl_from_command_line(cmd_line_specs, smv)


def check_nusmv_output(raw_output: str):
    lines_output: List[str] = raw_output.splitlines()
    error: bool = False

    for line in lines_output:
        if line.startswith("-- specification") and "is false" in line:
            error = True

    if error is True or VERBOSE:
        for line in lines_output:
            print(line)

    if error is True:
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
    except subprocess.CalledProcessError as err:
        logger.error(err.output.decode() + err.stderr.decode())
        sys.exit(255)


def main():
    global VERBOSE
    args = parse_command()

    if args.verbosity:
        VERBOSE = True
        logger.setLevel(logging.DEBUG)

    logger.debug(f"Current path: {Path.cwd()}")

    spec: Path = args.spec
    fsm_system: Path = spec.parent / (spec.stem + ".scy")
    smv_system: Path = spec.parent / f"{spec.stem}.smv"
    smv_integration: Path = spec.parent / f"{spec.stem}-i.smv"
    uses: Path = args.uses

    if args.skip_mc and args.skip_direct:
        print("ERROR! At least on checking is required!")
        sys.exit(255)

    # print(f"Running direct verification...", end="")
    device, assembled_device = create_fsm_system_model(
        spec, uses, fsm_system, args.skip_direct
    )

    # if not args.skip_direct:
    #     print("OK!")
    # else:
    #     print(f"SKIP!")

    if not args.skip_mc:
        create_system_model(device, fsm_system, smv_system)

        # print("Model checking system...", end="")
        logger.debug("Model checking system...")
        model_check(smv_system)
        logger.debug("OK!")

        if assembled_device.internal is not None:
            fsm_integration: Path = spec.parent / (spec.stem + "-i.scy")
            logger.debug(f"Dumping FSM integration model: {fsm_integration}")
            shelleyc.dump_integration_model(assembled_device, fsm_integration)
            assert fsm_integration.exists()

            subsystems: Mapping[str, Path] = dict(get_instances(args.spec, args.uses))

            if args.split_usage:
                logger.debug("Split usage is enabled")
                create_split_usage_model(spec, fsm_integration, subsystems)
            else:
                logger.debug("Split usage is disabled")
                create_instance_model(
                    fsm_integration, smv_integration, subsystems, args.formula
                )

            # print("Model checking integration...", end="")
            logger.debug("Model checking integration...")
            model_check(smv_integration)
            logger.debug("OK!")
