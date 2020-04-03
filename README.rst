***************
Shelley checker
***************

Run compiler
############

.. code-block:: shell

   # show all otions
   python3 -m appcompiler -h

   # compile a device without dependencies (uses)
   python3 -m appcompiler -d examples/button.yaml

   # compile a device with dependencies (uses)
   python3 -m appcompiler -u examples/button.sc:Button examples/led.sc:Led examples/timer.sc:Timer -d examples/desklamp.yaml

   # user-defined output folder (-o), verbose (-v)
   python3 -m appcompiler -o examples/compiled  -u examples/compiled/button.sc:Button examples/compiled/led.sc:Led examples/compiled/timer.sc:Timer -d examples/desklamp.yaml -v

   # compile a device in binary mode
   python3 -m appcompiler -b -d examples/button.yaml

   # visualize a compiled device
   python3 viz.py < examples/desklamp.scy | xdot -

.. warning:: To compile composite devices, please compile all dependency components first.


