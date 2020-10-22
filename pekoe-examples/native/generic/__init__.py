from dispatchers import native_dispatcher
from events import NativeEvent


class Native:
    callbacks_map = None  # there is a map for each native driver

    def __init__(self):
        self.callbacks_map = {}  # type: Dict[int, Callable[[], None]]

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
        if event_id in self.callbacks_map.keys():
            event_instance = NativeEvent(lambda: self.event_callback(event_id))
            native_dispatcher.add_event(event_instance)
            # no need to unsubscribe here, do it when consuming the event

    def event_callback(self, event_id: int):
        if event_id in self.callbacks_map.keys():
            driver_callback = self.callbacks_map.pop(event_id)  # unsubscribe
            driver_callback()
