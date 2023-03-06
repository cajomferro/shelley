# Shelley, a framework for model checking call ordering on hierarchical systems

![https://github.com/psf/black](https://img.shields.io/badge/code%20style-black-000000.svg)

### Try it

The easiest way to use Shelley is by using Docker.

```
make docker-build
make docker-run # this gets you inside a full-prepared environment
```

### Demo


### Examples


### Available tools

```shell
# show all options
shelleyc -h

# compile a device without dependencies (uses)
shelleyc -d examples/button.yml

# compile a device with dependencies (uses)
shelleyc -u examples/button.scy:Button examples/led.scy:Led examples/timer.scy:Timer -d examples/desklamp.yml

# visualize a compiled device using xdot
shelleyv -o examples/desklamp/desklamp.gv examples/desklamp/desklamp.scy
dot -Tpdf -o examples/desklamp/desklamp.pdf examples/desklamp/desklamp.gv

# Verify integration using the NuSMV model checker
shelleymc -s examples/desklamp/desklamp.shy -u examples/desklamp/uses.yml --integration-check

# Generate the integration model examples/desklamp/desklamp/controller.smv and adding an LTLf formula on the end
shelleymc -s examples/desklamp/desklamp.shy -u examples/desklamp/uses.yml --formula a.on "X t.begin"
```

