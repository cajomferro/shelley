from dispatchers import dispatcher
from events import Event
from typing import (
    Dict,
    Callable,
)  # https://docs.python.org/3/library/typing.html#callable


class Device:
    driver_id = None
    callbacks_map = None  # there is a map for each device

    def __init__(self, driver_id: str):
        self.driver_id = driver_id
        self.callbacks_map = {}  # type: Dict[int, Callable[[], None]]

    def unsubscribe(self):
        """
        Unsubscribe all
        :return:
        """
        self.callbacks_map = {}

    def subscribe(self, event_id=None, device_callback=None):
        """

        :param event_id: event id
        :type event_id: int
        :param device_callback:
        :return:
        """
        # what if the event already exists? Can this raise a conflict somehow?
        self.callbacks_map[event_id] = device_callback

    def raise_event(self, event_id: int):
        if (
            event_id in self.callbacks_map.keys()
        ):  # do not raise if no one has subscribed
            event_instance = Event(lambda: self.event_callback(event_id))
            dispatcher.add_event(event_instance)
            # no need to unsubscribe here, do it when consuming the event

    def event_callback(self, event_id: int):
        if event_id in self.callbacks_map.keys():
            device_callback = self.callbacks_map.pop(event_id)  # unsubscribe
            device_callback()
