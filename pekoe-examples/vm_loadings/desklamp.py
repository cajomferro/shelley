from dispatchers import native_dispatcher, dispatcher
from native.arduino.analog_input import ArduinoAnalogInput
from native.arduino.digital_output import ArduinoDigitalOutput
from native.arduino.timer import ArduinoTimer
from devices.timer import TimerDevice
from devices.button import ButtonDevice
from devices.led import LEDDevice
from devices.desklamp import DeskLampDevice

STOP_MACHINE = False

desklamp = None  # type: DeskLampDevice


def register_drivers():
    timer_native = ArduinoTimer()
    timer = TimerDevice("timer", timer_native)
    dispatcher.register_driver(timer)

    button_pin_number = 3
    button_native = ArduinoAnalogInput(button_pin_number)
    button = ButtonDevice("button", button_native)
    dispatcher.register_driver(button)

    ledA_pin_number = 13
    ledA_native = ArduinoDigitalOutput(ledA_pin_number)
    ledA = LEDDevice(ledA_native)
    dispatcher.register_driver(ledA)

    ledB_pin_number = 12
    ledB_native = ArduinoDigitalOutput(ledB_pin_number)
    ledB = LEDDevice(ledB_native)
    dispatcher.register_driver(ledB)

    desklamp = DeskLampDevice("lamp", timer, button, ledA, ledB)
    dispatcher.register_driver(desklamp)


if __name__ == "__main__":
    register_drivers()

    while STOP_MACHINE is not True:
        native_dispatcher.next()
        dispatcher.next()
