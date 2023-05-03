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
# python generate_subsystem_model.py ../integration_controller-i.scy ../integration_controller-d-b.scy b
# cd ..
# shelleyv --format png integration_controller-d-b.scy -o integration_controller-d-b.png --nfa-no-sink