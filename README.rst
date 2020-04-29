***************
Shelley checker
***************

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black

Installation
############

.. code-block:: shell

   poetry install

Run tools
#########

.. code-block:: shell

   # show all otions
   shelleyc -h

   # compile a device without dependencies (uses)
   shelleyc -d examples/button.yml

   # compile a device with dependencies (uses)
   shelleyc -u examples/button.scy:Button examples/led.scy:Led examples/timer.scy:Timer -d examples/desklamp.yml

   # visualize a compiled device using xdot
   shelleyv -o examples/desklamp/desklamp.gv examples/desklamp/desklamp.scy
   dot -Tpdf -o examples/desklamp/desklamp.pdf examples/desklamp/desklamp.gv

.. warning:: To compile composite devices, please compile all dependency components first.

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
