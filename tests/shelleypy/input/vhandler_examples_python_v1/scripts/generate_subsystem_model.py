import sys
from pathlib import Path
from shelley.shelleyv import shelleyv


integration_fsm: Path = Path(sys.argv[1])
submodel_fsm: Path = Path(sys.argv[2])
project_prefix: str = str(sys.argv[3])

shelleyv.dump_subsystem_fsm(integration_fsm, submodel_fsm, f"{project_prefix}.")

# This requires valvehandler to have claims with subsystem checks!
# Example:
# make clean && make
# cd scripts
# python generate_subsystem_model.py ../vhandler_extended-i.scy ../vhandler_extended-d-a.scy a
# cd ..
# shelleyv --format png vhandler_extended-d-a.scy -o vhandler_extended-d-a.png --nfa-no-sink