import logging
from shelley.parser import parse
import sys
import yaml
import argparse
import subprocess
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("shelleymc")


def get_instances(dev_filename, uses_filename):
    uses = yaml.safe_load(open(uses_filename)) if uses_filename is not None else dict()
    dev = parse(open(dev_filename))
    for (k, v) in dev.components:
        filename = Path(uses[v])
        yield (k, filename.parent / f"{filename.stem}.shy")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", "-s", help="Shelley specification.", required=True)
    parser.add_argument("--uses", "-u", help="The uses YAML file.")
    parser.add_argument("--formula", "-f", nargs="*", help="Give a correctness claim", default=[])
    parser.add_argument("--integration-check", action="store_true")
    parser.add_argument("--skip-mc", action="store_true")
    parser.add_argument("--split-usage", action="store_true", help="Check the usage of each subsystem separately.")
    parser.add_argument("--skip-integration-model", action="store_true")
    parser.add_argument(
        "-v", "--verbosity", help="increase output verbosity", action="store_true"
    )
    parser.add_argument(
        "--silent", help="hide NuSMV output (useful for benchmarking)", action="store_false"
    )
    args = parser.parse_args()

    if args.verbosity:
        logger.setLevel(logging.DEBUG)

    subsystems = dict(get_instances(args.spec, args.uses))
    spec = Path(args.spec)
    integration = spec.parent / (spec.stem + "-i.scy")
    logger.debug(f"Creating integration model: {integration}")
    subprocess.check_call([
        "shelleyc",
        "-u",
        args.uses,
        "-d",
        args.spec,
        "--skip-checks",
        "--integration",
        str(integration)
    ])
    assert integration.exists()
    if (args.integration_check and not args.split_usage) or not args.skip_integration_model:
        integration_model = spec.parent / f"{spec.stem}.smv"
        logger.debug(f"Creating NuSMV model: {integration_model}")
        subprocess.check_call([
            "shelleyv",
            str(integration),
            "--dfa",
            "-f",
            "smv",
            "-o",
            str(integration_model)
        ], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        if len(args.formula) > 0:
            logger.debug("Appending LTL formula:", " & ".join(args.formula))
            checks = subprocess.check_output([
                                                 "ltl",
                                                 "formula",
                                             ] + args.formula)
            with integration_model.open("a+") as fp:
                fp.write(checks.decode("utf-8"))

    if args.integration_check:
        if args.split_usage:
            for (instance_name, instance_spec) in subsystems.items():
                # Create the integration SMV file
                usage_model = spec.parent / f"{spec.stem}-{instance_name}.smv"
                logger.debug("creating", usage_model)
                subprocess.check_call([
                    "shelleyv",
                    str(integration),
                    "--dfa",
                    "-f",
                    "smv",
                    "--filter",
                    instance_name + ".*",
                    "-o",
                    str(usage_model)
                ])
                checks = subprocess.check_output([
                    "ltl",
                    "instance",
                    "--spec",
                    str(instance_spec),
                    "--name",
                    instance_name
                ])
                logger.debug("Model checking usage of", instance_name)
                with usage_model.open("a+") as fp:
                    fp.write(checks.decode("utf-8"))
                try:
                    subprocess.check_call([
                        "NuSMV",
                        str(usage_model),
                    ])
                except subprocess.CalledProcessError:
                    sys.exit(255)
        else:
            with integration_model.open("a+") as fp:
                for (instance_name, instance_spec) in subsystems.items():
                    logger.debug(f"Append LTL usage of {instance_name}")
                    checks = subprocess.check_output([
                        "ltl",
                        "instance",
                        "--spec",
                        str(instance_spec),
                        "--name",
                        instance_name
                    ])
                    fp.write(checks.decode("utf-8"))
    if not args.skip_mc:
        logger.debug("Model checking integration...")
        try:
            subprocess.check_call([
                "NuSMV",
                str(integration_model),
            ],
                stdout=None if args.silent else subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            logger.error(exc_info=True)
            sys.exit(255)
