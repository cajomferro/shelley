from shelley.parser import parse
import sys
import yaml
import argparse
import subprocess
from pathlib import Path

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
    parser.add_argument("--skip-integration-model", action="store_true")
    args = parser.parse_args()
    subsystems = dict(get_instances(args.spec, args.uses))
    spec = Path(args.spec)
    integration = spec.parent / (spec.stem + "-i.scy")
    if not integration.exists():
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
    if not args.skip_integration_model:
        integration_model = spec.parent / f"{spec.stem}.smv"
        subprocess.check_call([
            "shelleyv",
            str(integration),
            "--dfa",
            "-f",
            "smv",
            "-o",
            str(integration_model)
        ])
        if len(args.formula) > 0:
            checks = subprocess.check_output([
                "ltl",
                "formula",
            ] + args.formula)
            with integration_model.open("a+") as fp:
                fp.write(checks.decode("utf-8"))

    if args.integration_check:
        for (instance_name, instance_spec) in subsystems.items():
            # Create the integration SMV file
            usage_model = spec.parent / f"{spec.stem}-{instance_name}.smv"
            print("creating", usage_model)
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
            print("Model checking usage of", instance_name)
            with usage_model.open("a+") as fp:
                fp.write(checks.decode("utf-8"))
            try:
                subprocess.check_call([
                    "NuSMV",
                    str(usage_model),
                ])
            except subprocess.CalledProcessError:
                sys.exit(255)
