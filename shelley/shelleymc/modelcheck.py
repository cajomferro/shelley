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
from dataclasses import dataclass, field
from shelley.shelleymc.ltlf import Spec, Formula

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
        filename = Path(uses_path.parent / uses[v])
        yield (k, filename.parent / f"{filename.stem}.shy")

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
        print(err.output.decode() + err.stderr.decode())
        sys.exit(255)



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


@dataclass
class ModelChecker:
    file: Path
    specs: List[Spec] = field(default_factory=list)
    def add(self, spec:Spec):
        self.specs.append(spec)

    def __len__(self):
        return sum(len(s) for s in self.specs)

    def run(self):
        count = len(self)
        if count == 0:
            logger.debug(f"Skip model checking {self.path} (0 formulas)")
            return
        with self.file.open("a+") as fp:
            for spec in self.specs:
                logger.debug(spec)
                spec.dump(fp)
        model_check(self.file)

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
            print(err)
        sys.exit(255)

    assert fsm_system.exists()
    logger.debug(f"Created FSM system model")
    if assembled_device.internal is not None:
        logger.debug(f"Created FSM integration model")

    return device, assembled_device


def check_system(dev: Device, fsm: Path, smv: Path, system_validity:bool=True):
    logger.debug(f"Creating NuSMV system model: {smv}")
    shelleyv.fsm2smv(fsm, smv, ctl_compatible=True)
    mc = ModelChecker(smv)
    spec = Spec([], "SYSTEM CHECKS")
    for f in dev.system_formulae:
        spec.formlae.append(LTL_F(f))
    mc.add(spec)

    if system_validity:
        logger.debug(f"Generating system specs: {fsm}")
        mc.add(ltlf.generate_system_spec(dev))
    mc.run()


def check_usage(
    system_spec: Path,
    integration: Path,
    subsystems: Mapping[str, Path],
    subsystem_formulae: List[Tuple[str,Formula]],
    integration_validity:bool=True,
) -> None:
    if not integration_check:
        logger.debug(f"Integration validity will *NOT* be enforced by the model checker.")

    for (instance_name, instance_spec) in subsystems.items():
        dev: Device = shelley_lark_parser.parse(instance_spec)
        # Create the integration SMV file
        smv_path = system_spec.parent / f"{system_spec.stem}-d-{instance_name}.smv"
        mc = ModelChecker(smv_path)
        mc.add(ltlf.generate_subsystem_checks(subsystem_formulae, instance_name))
        if integration_validity:
            logger.debug(f"Adding integration check for {instance_name}")
            mc.add(ltlf.generate_usage_validity(dev, prefix=None))
        mc.add(ltlf.generate_enforce_usage(dev, prefix=None))
        if len(mc) == 0:
            logger.debug(f"Skip model checking usage (0 formulas): '{instance_name}'")
            continue
        logger.debug(f"Creating usage behavior for '{instance_name}': {smv_path}")
        shelleyv.fsm2smv(
            fsm_model=integration,
            smv_model=smv_path,
            project_prefix=instance_name + ".",
        )
        logger.debug(f"Model checking usage behavior: '{instance_name}'")
        mc.run()


def check_integration(
    dev: Device,
    fsm: Path,
    smv: Path,
    subsystems: Mapping[str, Path],
    cmd_line_specs: List[str],
    integration_check:bool=True
):
    mc = ModelChecker(smv)
    spec = ltlf.Spec(formulae=[], comment="COMMAND LINE SPECS")
    for entry in cmd_line_specs:
        logger.debug(f"Appending LTL formula from cmd line: {entry}")
        spec.formulae.append(LTL_F(ltlf.parse_ltlf_formulae(entry)))
    mc.add(spec)
    spec = ltlf.Spec(formulae=[], comment="INTEGRATION CHECKS")
    for entry in dev.system_formulae:
        logger.debug(f"Appending LTL formula from system checks: {entry}")
        spec.formulae.append(LTL_F(entry))
    mc.add(spec)
    if len(mc) > 0:
        # Create the integration SMV
        logger.debug(f"Creating integration file: {smv}")
        shelleyv.fsm2smv(fsm, smv)
        logger.debug("Model checking integration...")
        mc.run()


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

    if not args.skip_mc:
        check_system(device, fsm_system, smv_system, system_validity=args.skip_direct)
        if assembled_device.internal is not None:
            if not args.skip_direct and len(device.enforce_formulae) == 0 and len(args.formula) == 0:
                logger.debug("Skip model check integration, because: integration checks are DIRECT, 0 enforces, 0 user claims.")
                return
            fsm_integration: Path = spec.parent / (spec.stem + "-i.scy")
            logger.debug(f"Dumping FSM integration model: {fsm_integration}")
            shelleyc.dump_integration_model(assembled_device, fsm_integration)
            assert fsm_integration.exists()

            subsystems: Mapping[str, Path] = dict(get_instances(args.spec, args.uses))

            logger.debug("Check integration validity")
            check_usage(
                system_spec=spec,
                integration=fsm_integration,
                subsystems=subsystems,
                integration_validity=args.skip_direct,
                subsystem_formulae=device.subsystem_formulae,
            )

            logger.debug("Check user correctness claims")
            check_integration(
                device,
                fsm_integration,
                smv_integration,
                subsystems,
                args.formula,
            )

            # print("Model checking integration...", end="")
            logger.debug("OK!")
