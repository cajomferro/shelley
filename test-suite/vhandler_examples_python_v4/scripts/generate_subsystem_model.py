import sys
from pathlib import Path
from shelley.shelleyv import shelleyv


integration_fsm: Path = Path(sys.argv[1])
submodel_fsm: Path = Path(sys.argv[2])
project_prefix: str = str(sys.argv[3])

shelleyv.dump_subsystem_fsm(integration_fsm, submodel_fsm, f"{project_prefix}.")

# Example: python generate_subsystem_model.py valvehandler-i.scy valvehandler-d-t.scy t
