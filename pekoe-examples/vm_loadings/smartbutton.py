from decorators import program, callback
from events import Events

smart_button = None  # just for editor


@program
class CoolButton:
    def __init__(self):
        smart_button  # @driver(SmartButton)
        smart_button.subscribe(
            driver_callback=self.say_hello,
            event=Events.SMART_BUTTON_BUTTON_PRESSED_ONCE,
        )

    @callback
    def say_hello(self):
        print("Hello!")


if __name__ == "__main__":
    CoolButton()
