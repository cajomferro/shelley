***************
Shelley checker
***************

Run compiler
############

.. code-block:: shell

   # show all otions
   python -m appcompiler -h

   # compile a device without dependencies (uses)
   python -m appcompiler -d examples/button.yaml

   # compile a device with dependencies (uses)
   python -m appcompiler -u examples/compiled/button.sc:Button examples/compiled/led.sc:Led examples/compiled/timer.sc:Timer -d examples/desklamp.yaml

   # user-defined output folder (-o), verbose (-v)
   python -m appcompiler -o examples/compiled  -u examples/compiled/button.sc:Button examples/compiled/led.sc:Led examples/compiled/timer.sc:Timer -d examples/desklamp.yaml -v

   # compile a device in binary mode
   python -m appcompiler -b -d examples/button.yaml

.. warning:: To compile composite devices, please compile all dependency components first.


