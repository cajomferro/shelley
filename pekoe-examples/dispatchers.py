from collections import deque
from events import Event, NativeEvent


class NativeDispatcher:
    drivers = None
    events_queue = None

    def __init__(self):
        self.drivers = {}
        self.events_queue = deque()

    def next(self):
        event = None  # type: NativeEvent
        try:
            event = (
                self.events_queue.popleft()
            )  # we could also order it by timestamp if we want :)
            event.callback()
        except IndexError:
            pass

    def add_event(self, event: NativeEvent):
        self.events_queue.append(event)


class Dispatcher:
    drivers = None
    events_queue = None

    def __init__(self):
        self.drivers = {}
        self.events_queue = deque()

    def next(self):
        event = None  # type: Event
        try:
            event = (
                self.events_queue.popleft()
            )  # we could also order it by timestamp if we want :)
            event.callback()
        except IndexError:
            pass

    def add_event(self, event: Event):
        self.events_queue.append(event)

    def register_driver(self, driver_instance):
        self.drivers[driver_instance.driver_name] = driver_instance


native_dispatcher = NativeDispatcher()  # singleton
dispatcher = Dispatcher()  # singleton

#
# for driver_name, driver_instance in self.drivers.items():
#     events_queue = driver_instance.events_queue
#     callbacks_map = driver_instance.callbacks_map
#     if events_queue.count() > 0:
#         event = events_queue.popleft()
#         if event in callbacks_map.keys():
#             driver_callback = callbacks_map.pop(event)  # unsubscribe
#             driver_callback()
