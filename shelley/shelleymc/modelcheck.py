import logging
from typing import Tuple
from shelley.parsers import shelley_lark_parser, ltlf_lark_parser
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
from shelley.shelleymc.ltlf import Spec, Formula, LTL_F, Next, LTL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("shelleymc")
logger_shelleyc = logging.getLogger("shelleyc")
logger_shelleyv = logging.getLogger("shelleyv")
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


def model_check(smv_path: Path):
    try:
        nusmv_call = [
            "NuSMV",
            str(smv_path),
        ]
        logger.debug(" ".join(nusmv_call))
        cp: subprocess.CompletedProcess = subprocess.run(
            nusmv_call, capture_output=True, check=True
        )
        return check_nusmv_output(cp.stdout.decode())
    except subprocess.CalledProcessError as err:
        print(err.output.decode() + err.stderr.decode())
        sys.exit(255)


def parse_states(trace):
    state = dict()
    result = []
    pending = False
    for line in trace:
        if line.startswith("-> State"):
            if len(state) == 0:
                continue
            result.append(state)
            state = dict(state)
            pending = True
        elif line.startswith("-- Loop"):
            continue
        else:
            k, v = line.split(" = ", 1)
            state[k.strip()] = v.strip()
            pending = True
    if pending:
        result.append(state)
    return result


def parse_trace(trace):
    actions = []
    for state in parse_states(trace):
        if state["_state"] == "-1":
            continue
        if state["_eos"] == "TRUE":
            break
        actions.append(state["_action"])
    return actions


def check_nusmv_output(raw_output: str):
    lines_output: List[str] = raw_output.splitlines()
    error: bool = False
    specs = []
    results = []
    handle_trace = False
    trace = []
    for line in lines_output:
        if line.startswith("Trace ") or line.startswith("-- as demonstrated by "):
            continue
        if handle_trace:
            if line.startswith("-- specification"):
                handle_trace = False
                results.append(parse_trace(trace))
                trace = None
            else:
                trace.append(line.strip())
                continue
        if line.startswith("-- specification"):
            line = line[len("-- specification") :]
            line, answer = line.rsplit(" is ")
            result = answer.strip() == "true"
            specs.append(line.strip())
            if result:
                results.append(None)
            else:
                error = True
                handle_trace = True
                trace = []
    if len(specs) > len(results):
        results.append(parse_trace(trace))
    if error:
        logger.debug(raw_output)
    if error:
        return list(zip(specs, results))
    else:
        return None


@dataclass
class ModelChecker:
    file: Path
    specs: List[Spec] = field(default_factory=list)

    def add(self, spec: Spec):
        self.specs.append(spec)

    def __len__(self):
        return sum(len(s) for s in self.specs)

    def run(self):
        count = len(self)
        if count == 0:
            logger.debug(f"Skip model checking {self.file} (0 formulas)")
            return
        with self.file.open("a+") as fp:
            for spec in self.specs:
                logger.debug(spec)
                spec.dump(fp)
        result = model_check(self.file)
        if result is not None:
            specs = []
            for s in self.specs:  # [::-1]:  # NuSMV lists CTL before LTL
                for f in s.formulae:
                    specs.append((f, s.comment))
            for ((formula, comment), (raw_formula, trace)) in zip(specs, result):
                if trace is not None:
                    print("Error in specification:", comment, file=sys.stderr)
                    print(
                        "Formula:",
                        ltlf_lark_parser.dumps(formula, nusvm_strict=False),
                        file=sys.stderr,
                    )
                    trace_str = "; ".join(trace) if len(trace) > 0 else "(empty)"
                    print("Counter example:", trace_str, file=sys.stderr)
                    sys.exit(255)


def create_fsm_system_model(
    spec: Path,
    uses: Path,
    fsm_system: Path,
    skip_direct_checks: bool = False,
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
            check_ambiguity=False,
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


def check_system(dev: Device, fsm: Path, smv: Path, system_validity: bool = True):
    mc = ModelChecker(smv)
    spec = Spec([], "SYSTEM CHECKS")
    for f in dev.system_formulae:
        # Since the model is CTL-compatible, then we need to prefix each
        # LTL formula with a next, so we skip the dummy initial state.
        spec.formulae.append(LTL(Next(LTL_F(f))))
    mc.add(spec)
    if system_validity:
        logger.debug(f"Generating system specs: {fsm}")
        mc.add(ltlf.generate_system_spec(dev))
    if len(mc) > 0:
        logger.debug(f"Creating NuSMV system model: {smv}")
        shelleyv.fsm2smv(fsm, smv, ctl_compatible=True)
        mc.run()
    else:
        logger.debug("No model checking needed for system.")


def check_usage(
    system_spec: Path,
    integration: Path,
    subsystems: Mapping[str, Device],
    subsystem_formulae: List[Tuple[str, Formula]],
    integration_validity: bool = True,
) -> None:
    if not integration_validity:
        logger.debug(
            f"Integration validity will *NOT* be enforced by the model checker."
        )

    for (instance_name, dev) in subsystems.items():
        # Create the integration SMV file
        smv_path = system_spec.parent / f"{system_spec.stem}-d-{instance_name}.smv"
        mc = ModelChecker(smv_path)
        mc.add(ltlf.generate_subsystem_checks(subsystem_formulae, instance_name))
        if integration_validity:
            logger.debug(f"Adding integration check for {instance_name}")
            mc.add(ltlf.generate_usage_validity(dev, prefix=instance_name))
        mc.add(ltlf.generate_enforce_usage(dev, prefix=instance_name))
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
):
    mc = ModelChecker(smv)
    spec = ltlf.Spec(formulae=[], comment="INTEGRATION CHECKS")
    for entry in dev.integration_formulae:
        logger.debug(f"Appending LTL formula from integration checks: {entry}")
        spec.formulae.append(LTL_F(entry))
    mc.add(spec)
    if len(mc) > 0:
        # Create the integration SMV
        logger.debug(f"Creating integration file: {smv}")
        shelleyv.fsm2smv(fsm, smv)
        logger.debug("Model checking integration...")
        mc.run()
    else:
        logger.debug(f"Skip model checking integration (0 formulas)")


def count_integration_claims(dev, subsystems):
    total = 0
    total += len(dev.integration_formulae)
    total += len(dev.subsystem_formulae)
    for d in subsystems.values():
        total += len(d.enforce_formulae)
    return total


def parse_command():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--spec", "-s", type=Path, help="Shelley specification.", required=True
    )
    parser.add_argument("--uses", "-u", type=Path, help="The uses YAML file.")
    parser.add_argument("--skip-mc", action="store_true")
    parser.add_argument("--skip-direct", action="store_true")
    parser.add_argument(
        "-v", "--verbosity", help="increase output verbosity", action="store_true"
    )

    return parser.parse_args()


def main():
    global VERBOSE
    args = parse_command()

    if args.verbosity:
        VERBOSE = True
        logger_shelleyc.setLevel(logging.DEBUG)
        logger_shelleyv.setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)

    logger.debug(f"Current path: {Path.cwd()}")

    spec: Path = args.spec
    fsm_system: Path = spec.parent / (spec.stem + ".scy")
    smv_system: Path = spec.parent / f"{spec.stem}.smv"
    smv_integration: Path = spec.parent / f"{spec.stem}-i.smv"
    uses: Path = args.uses

    if args.skip_mc and args.skip_direct:
        print("ERROR! Choose one check-validity algorithm only!")
        sys.exit(255)

    # print(f"Running direct verification...", end="")
    device, assembled_device = create_fsm_system_model(
        spec, uses, fsm_system, args.skip_direct
    )

    if args.skip_mc:
        logger.debug("Skipping model checking with --skip-mc.")
        return

    check_system(device, fsm_system, smv_system, system_validity=args.skip_direct)
    if assembled_device.internal is None:
        logger.debug("We found a base system, no integration to check needed.")
        return

    subsystems: Mapping[str, Device] = dict(
        (k, shelley_lark_parser.parse(v))
        for k, v in get_instances(args.spec, args.uses)
    )
    user_claims = count_integration_claims(device, subsystems)
    logger.debug(
        f"Model check integration validity: {args.skip_direct}; user claims: {user_claims}"
    )
    if not args.skip_direct and user_claims == 0:
        logger.debug("No model checking needed for integration.")
        return

    fsm_integration: Path = spec.parent / (spec.stem + "-i.scy")
    logger.debug(f"Saving FSM integration model to disk: {fsm_integration}")
    shelleyc.dump_integration_model(assembled_device, fsm_integration)
    assert fsm_integration.exists()

    logger.debug("Check the usage of each subsystem")
    check_usage(
        system_spec=spec,
        integration=fsm_integration,
        subsystems=subsystems,
        integration_validity=args.skip_direct,
        subsystem_formulae=device.subsystem_formulae,
    )

    logger.debug("Check integration claims")
    check_integration(
        device,
        fsm_integration,
        smv_integration,
    )
