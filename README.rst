***************
Shelley checker
***************

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black

Installation
############

.. warning:: You will need to install `poetry <https://python-poetry.org/docs/#installation>`_ and graphviz dot tool (for visualizing examples). Make sure you install poetry with the appropriate Python version (>=3.7). For more info on how to install poetry with pyenv `follow this link <https://python-poetry.org/docs/managing-environments/>`_.

.. warning:: If you intend to use the LTL model checking capabilities of Shelley, you will need to instal NuSMV first.

.. code-block:: shell

   # To install the shelley-checker
   poetry install

.. code-block:: shell

   # To install NuSMV on macOS
   brew install nu-smv


Run tools
#########

.. code-block:: shell

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
   shelleymc -s examples/desklamp/desklamp.shy -u examples/desklamp/uses.yml --integration-check --skip-integration-mode

	# Generate the integration model examples/desklamp/desklamp/controller.smv and adding an LTLf formula on the end
   shelleymc -s examples/desklamp/desklamp.shy -u examples/desklamp/uses.yml --formula "X begin"

.. warning:: To compile composite devices, please compile all dependency components first.

Get project stats
######################

.. code-block:: shell

    radon raw shelley -s -O stats.txt

Useful poetry commands
######################

.. code-block:: shell

    # show env info (useful for configuring your preferred IDE)
    # Example configurations for PyCharm: https://www.reddit.com/r/pycharm/comments/elga2z/using_pycharm_for_poetrybased_projects/
    poetry env info


    # these are all equivalent
    poetry run python -m shelleyc
    poetry run shelleyc
    shelleyc

Helpful tips and commands
#########################

Renaming words in several files
-------------------------------

* https://www.cyberciti.biz/faq/how-to-use-sed-to-find-and-replace-text-in-files-in-linux-unix-shell/
* https://serverfault.com/questions/172806/use-sed-recursively-in-linux
* https://stackoverflow.com/questions/19456518/invalid-command-code-despite-escaping-periods-using-sed
* https://stackoverflow.com/questions/19242275/re-error-illegal-byte-sequence-on-mac-os-x

In this example, we replace the word "micro" by "integration".

.. code-block:: shell

    export LC_CTYPE=C
    export LANG=C
    find . -type f -print0 | xargs -0 sed -i '' -e "s/micro:/integration:/g"

