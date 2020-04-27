***************
Shelley checker
***************

Run tools
############

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


