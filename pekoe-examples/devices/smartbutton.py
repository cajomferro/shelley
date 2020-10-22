from decorators import callback, raise_event
from devices import Device
from devices.button import ButtonDevice as Button
from devices.timer import TimerDevice as Timer


class SmartButtonDriver(Device):  # implements device SmartButton

    PRESSED_ONCE = 0
    PRESSED_TWICE = 1
    PRESSED_LONG = 2

    timer = None  # type: Timer
    button = None  # type: Button

    def __init__(self, driver_id: str, timer: Timer, button: Button):
        Device.__init__(self, driver_id)
        self.timer = timer
        self.button = button
        self.button.subscribe(device_callback=self.on_button_pressed, event=Button.PRESSED)

    @callback(Button.PRESSED)
    def on_button_pressed(self):
        self.timer.subscribe(device_callback=self.on_timer_started, event=Timer.STARTED)
        self.timer.start(5)  # this is the predefined duration for the buttonPressedLong (5 seconds)

    @callback(Timer.STARTED)
    def on_timer_started(self):
        self.timer.subscribe(device_callback=self.on_timer_timeout_long, event=Timer.TIMEOUT)
        self.button.subscribe(device_callback=self.on_button_released, event=Button.RELEASED)

    @callback(Button.RELEASED)
    @raise_event(PRESSED_LONG)
    def on_timer_timeout_long(self):
        self.button.subscribe(device_callback=self.on_button_pressed, event=Button.PRESSED)
        self.raise_event(self.PRESSED_LONG)

    @callback(Button.RELEASED)
    def on_button_released(self):
        self.timer.subscribe(device_callback=self.on_timer_canceled, event=Timer.CANCELED)
        self.timer.cancel()

    @callback(Timer.CANCELED)
    def on_timer_canceled(self):
        self.timer.subscribe(device_callback=self.on_timer_started_twice, event=Timer.STARTED)
        self.timer.start(0.5)  # this is the predefined duration for the buttonPressedOnce (half a second)

    @callback(Timer.STARTED)
    def on_timer_started_twice(self):
        self.timer.subscribe(device_callback=self.on_timer_timeout_twice, event=Timer.TIMEOUT)
        self.button.subscribe(device_callback=self.on_button_pressed_twice, event=Button.PRESSED)

    @callback(Timer.TIMEOUT)
    @raise_event(PRESSED_ONCE)
    def on_timer_timeout_twice(self):
        self.button.subscribe(device_callback=self.on_button_pressed, event=Button.PRESSED)
        self.raise_event(self.PRESSED_ONCE)

    @callback(Button.PRESSED)
    def on_button_pressed_twice(self):
        self.timer.cancel()
        self.button.subscribe(device_callback=self.on_button_released_twice, event=Button.RELEASED)

    @callback(Button.RELEASED)
    @raise_event(PRESSED_TWICE)
    def on_button_released_twice(self):
        self.button.subscribe(device_callback=self.on_button_pressed, event=Button.PRESSED)  # reset
        self.raise_event(self.PRESSED_TWICE)
