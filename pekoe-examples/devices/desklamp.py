from decorators import callback, raise_event, action
from devices import Device
from devices.led import LEDDevice as Led
from devices.button import ButtonDevice as Button
from devices.timer import TimerDevice as Timer


class DeskLampDevice(Device):  # implements device SmartButton

    LEVEL1 = 0
    LEVEL2 = 1
    STANDBY = 2

    ledA = None  # type: Led
    ledB = None  # type: Led
    timer = None  # type: Timer
    button = None  # type: Button

    def __init__(
        self, driver_id: str, timer: Timer, button: Button, ledA: Led, ledB: Led
    ):
        Device.__init__(self, driver_id)
        self.ledA = ledA
        self.ledB = ledB
        self.timer = timer
        self.button = button
        self.button.subscribe(
            event_id=Button.PRESSED, device_callback=self.on_button_pressed1
        )

    @callback(Button.PRESSED)
    def on_button_pressed1(self):
        self.button.subscribe(
            event_id=Button.RELEASED, device_callback=self.on_button_released1
        )

    @callback(Button.RELEASED)
    def on_button_released1(self):
        self.ledA.subscribe(event_id=Led.ON, device_callback=self.on_ledA_on)
        self.ledA.turn_on()

    @callback(Led.ON)
    def on_ledA_on(self):
        self.timer.subscribe(
            event_id=Timer.STARTED, device_callback=self.on_timer_started1
        )
        self.timer.start(5)

    @callback(Timer.STARTED)
    @raise_event(LEVEL1)
    def on_timer_started1(self):
        self.timer.subscribe(
            event_id=Timer.TIMEOUT, device_callback=self.on_timer_timeout
        )
        self.button.subscribe(
            event_id=Button.PRESSED, device_callback=self.on_button_pressed2
        )
        self.raise_event(self.LEVEL1)

    @callback(Timer.TIMEOUT)
    @raise_event(STANDBY)
    def on_timer_timeout(self):
        self.button.unsubscribe()  # TODO: is there an alternative for this??
        self.ledA.turn_off()
        self.ledB.turn_off()
        self.button.subscribe(
            event_id=Button.PRESSED, device_callback=self.on_button_pressed1
        )
        self.raise_event(self.STANDBY)

    @callback(Button.PRESSED)
    def on_button_pressed2(self):
        self.button.subscribe(
            event_id=Button.RELEASED, device_callback=self.on_button_released2
        )

    @callback(Button.RELEASED)
    def on_button_released2(self):
        self.timer.subscribe(
            event_id=Timer.CANCELED, device_callback=self.on_timer_canceled
        )
        self.timer.cancel()

    # FIRST ALTERNATIVE [CORRECT ACCORDING TO SPEC] --> PREPARING TO MATCH LEVEL2
    # [b.pressed, b.released, ledA.on, t.started, b.pressed, b.released, t.canceled, # ledB.on, t.started ]
    @callback(Timer.CANCELED)
    def on_timer_canceled(self):
        self.subscribe(event_id=Led.ON, device_callback=self.on_ledB_on)
        self.ledB.turn_on()

    # SECOND ALTERNATIVE [CORRECT ACCORDING TO SPEC] --> PREPARING TO MATCH STANDBY
    # [b.pressed, b.released, ledA.on, t.started, b.pressed, b.released, t.canceled, # ledA.off, ledB.off ]
    @callback(Timer.CANCELED)
    def on_timer_canceled(self):
        self.subscribe(event_id=Led.OFF, device_callback=self.on_ledA_off)
        self.ledA.turn_off()

    # THIRD ALTERNATIVE [CORRECT ACCORDING TO SPEC IF LED CAN TURN OFF REPEATEDLY] --> PREPARING TO MATCH STANDBY
    # [b.pressed, b.released, ledA.on, t.started, b.pressed, b.released, t.canceled, # ledB.off, ledA.off ]
    @callback(Timer.CANCELED)
    def on_timer_canceled(self):
        self.subscribe(event_id=Led.OFF, device_callback=self.on_ledB_off)
        self.ledB.turn_off()

    @callback(Led.ON)
    def on_ledB_on(self):
        self.timer.cancel()
        self.subscribe(event_id=Timer.STARTED, device_callback=self.on_timer_started2)
        self.timer.start(5)

    @callback(Timer.STARTED)
    @raise_event(LEVEL2)
    def on_timer_started2(self):
        self.subscribe(event_id=Timer.TIMEOUT, device_callback=self.on_timer_timeout)
        self.subscribe(event_id=Button.PRESSED, device_callback=self.on_button_pressed3)
        self.raise_event(self.LEVEL2)

    @callback(Button.PRESSED)
    @raise_event(STANDBY)
    def on_button_pressed3(self):
        self.timer.cancel()
        self.ledA.turn_off()
        self.ledB.turn_off()
        self.subscribe(event_id=Button.PRESSED, device_callback=self.on_button_pressed1)
        self.raise_event(self.STANDBY)
