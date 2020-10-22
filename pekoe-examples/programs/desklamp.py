# Program to operate a desklamp device
# Pressing the first time turns one LED on
# Pressing the second time turns both LEDs on
# Pressing the third time or after 5 seconds of inactivity both LEDs are turned off
from decorators import callback
from vm_loadings.desklamp import desklamp


class DeskLampExample:

    def __init__(self):
        desklamp.subscribe(event_id=desklamp.LEVEL1, device_callback=self.on_level1)
        print("Hello! Press the button to turn on")

    @callback(desklamp.LEVEL1)
    def on_level1(self):
        desklamp.subscribe(event_id=desklamp.LEVEL2, device_callback=self.on_level2)
        print("This is level 1")

    @callback(desklamp.LEVEL2)
    def on_level2(self):
        desklamp.subscribe(event_id=desklamp.STANDBY, device_callback=self.on_standby)
        print("This is level 2")

    @callback(desklamp.STANDBY)
    def on_standby(self):
        desklamp.subscribe(event_id=desklamp.LEVEL1, device_callback=self.on_level1)
        print("Saving batteries...")
