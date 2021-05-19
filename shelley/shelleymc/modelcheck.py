import logging
from shelley.parsers.shelley_lark_parser import parse
import sys
import yaml
import argparse
import subprocess
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("shelleymc")


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


def main():
    args = parse_command()

    if args.verbosity:
        logger.setLevel(logging.DEBUG)

    subsystems = dict(get_instances(args.spec, args.uses))
    spec = Path(args.spec)
    integration = spec.parent / (spec.stem + "-i.scy")
    logger.info(f"Creating integration model: {integration}")
    try:
        subprocess.check_call(
            [
                "shelleyc",
                "-u",
                args.uses,
                "-d",
                args.spec,
                "--skip-checks",
                "--integration",
                str(integration),
            ]
        )
    except subprocess.CalledProcessError:
        sys.exit(255)
    assert integration.exists()
    if (
        args.integration_check and not args.split_usage
    ) or not args.skip_integration_model:
        integration_model = spec.parent / f"{spec.stem}.smv"
        logger.info(f"Creating NuSMV model: {integration_model}")
        shelleyv_call = [
            "shelleyv",
            str(integration),
            "--dfa",
            "-f",
            "smv",
            "-o",
            str(integration_model),
        ]
        logger.debug(" ".join(shelleyv_call))
        subprocess.check_call(
            shelleyv_call, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
        )
        if len(args.formula) > 0:
            logger.info("Appending LTL formula:", " & ".join(args.formula))
            checks = subprocess.check_output(["ltl", "formula",] + args.formula)
            with integration_model.open("a+") as fp:
                fp.write(checks.decode("utf-8"))

    if args.integration_check:
        if args.split_usage:
            for (instance_name, instance_spec) in subsystems.items():
                # Create the integration SMV file
                usage_model = spec.parent / f"{spec.stem}-{instance_name}.smv"

                logger.debug("creating", usage_model)
                shelleyv_call = [
                    "shelleyv",
                    str(integration),
                    "--dfa",
                    "-f",
                    "smv",
                    "--filter",
                    instance_name + ".*",
                    "-o",
                    str(usage_model),
                ]
                logger.debug(" ".join(shelleyv_call))
                subprocess.check_call(shelleyv_call)

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
                with usage_model.open("a+") as fp:
                    fp.write(checks.decode("utf-8"))
                try:
                    subprocess.check_call(
                        ["NuSMV", str(usage_model),]
                    )
                except subprocess.CalledProcessError:
                    sys.exit(255)
        else:
            with integration_model.open("a+") as fp:
                for (instance_name, instance_spec) in subsystems.items():
                    logger.info(f"Append LTL usage of {instance_name}")
                    ltl_call = [
                        "ltl",
                        "instance",
                        "--spec",
                        str(instance_spec),
                        "--name",
                        instance_name,
                    ]
                    logger.debug(" ".join(ltl_call))
                    checks = subprocess.check_output(ltl_call)
                    fp.write(checks.decode("utf-8"))
    if not args.skip_mc:
        logger.info("Model checking integration...")
        try:
            nusmv_call = [
                "NuSMV",
                str(integration_model),
            ]
            logger.debug(" ".join(nusmv_call))
            subprocess.check_call(nusmv_call)
        except subprocess.CalledProcessError:
            sys.exit(255)
