# Shelley, a framework for model checking call ordering on hierarchical systems

![https://github.com/psf/black](https://img.shields.io/badge/code%20style-black-000000.svg)

### Update the project

`make pull`

### Building the project

`make -f host.mk build`

### Spawning a bash environment

`make -f host.mk run`

The commands above use docker which is the recommended way of using this project. 
The poetry.lock file is also mounted in order to be able to commit this file after updating.


### Run tools

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

---
**WARNING**

To compile composite devices, please compile all dependency components first.

---

# Helpful tips and commands

### Renaming words in several files

* https://www.cyberciti.biz/faq/how-to-use-sed-to-find-and-replace-text-in-files-in-linux-unix-shell/
* https://serverfault.com/questions/172806/use-sed-recursively-in-linux
* https://stackoverflow.com/questions/19456518/invalid-command-code-despite-escaping-periods-using-sed
* https://stackoverflow.com/questions/19242275/re-error-illegal-byte-sequence-on-mac-os-x

In this example, we replace the word "micro" by "integration".

```shell
 export LC_CTYPE=C
 export LANG=C
 find . -type f -print0 | xargs -0 sed -i '' -e "s/micro:/integration:/g"
```

### Count the number of Shelley specifications (recursively)


`find shelley-examples/ -name "*.shy" | wc -l`
   
   

### Setting Docker with PyCharm

[Debugging a Containerized Django App in PyCharm](https://testdriven.io/blog/django-debugging-pycharm).


### How to debug using PyCharm and Docker


![media/docker-debug-configuration.png](media/docker-debug-configuration.png)

### Get project stats

`radon raw shelley -s -O stats.txt`

### Model checking with NuSMV


In the following example, we assume the user is inside the folder `examples/paper_frankenstein_example`.

```shell
# Step 1 - Generate the integration behavior (FSM)
make controller.int

# Step 2 -
shelleyc -u uses.yml -d controller.shy --skip-checks -i controller.int --no-output
shelleyv controller.int --dfa -f svm -o controller.svm # Gerar o modelo da integração
Input: 25
DFA: 73
ltl -i timer.shy -p t > t.ltl
ltl -i valve.shy -p a > a.ltl
ltl -i valve.shy -p b > b.ltl
cat controller.svm t.ltl a.ltl b.ltl > cena.svm # Juntar tudo
nusvm cena.svm
```


### Useful poetry commands

````shell
 # show env info (useful for configuring your preferred IDE)
 # Example configurations for PyCharm: https://www.reddit.com/r/pycharm/comments/elga2z/using_pycharm_for_poetrybased_projects/
 poetry env info


 # these are all equivalent
 poetry run python -m shelleyc
 poetry run shelleyc
 shelleyc
```` 

# Manual Installation

---
**WARNING**

You will need to install [poetry](https://python-poetry.org/docs/#installation) and the graphviz dot tool (for 
visualizing examples). Make sure you install poetry with the appropriate Python version (>=3.10). For more info on 
how to install poetry with pyenv [follow this link](https://python-poetry.org/docs/managing-environments/).

If you intend to use the LTL model checking capabilities of Shelley, you will need to instal NuSMV first.

---

### To install shelley-checker

`poetry install`

### To install NuSMV on macOS

`brew install nu-smv`
