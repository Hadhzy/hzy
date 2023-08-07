import snegg.ei
from snegg.eis import EventType
from snegg.ei import EventType as ei_event_type
import snegg. ei as ei
from typing import TYPE_CHECKING
# This project
from hzy.client import Client


if TYPE_CHECKING:
    from queue import Queue


def handle_request(event, read_queue: Queue):
    """
    (source: https://gitlab.freedesktop.org/libinput/snegg/-/blob/main/examples/eis-demo-server.py)
    ### Arguments

    ### Returns

    """

    pointer = None
    abs  = None
    keyboard = None
    touchscreen = None

    if event.event_type == EventType.CLIENT_CONNECT:
        client = Client(event.client)
        client.connect()

        # create the seat
        seat = client.new_seat()
        seat.add()

        read_queue.put("client connected")

    if event.event_type == ei_event_type.SEAT_ADDED:
        seat = event.seat

        assert seat is not None

        seat.bind()

        read_queue.put("seat added")

    elif event.event_type == ei_event_type.DEVICE_ADDED:

        device = event.device
        assert device is not None

        if (
            pointer is None
            and ei.DeviceCapability.POINTER in device.capabilities
        ):
            pointer = device

        if (
            abs is None
            and ei.DeviceCapability.POINTER_ABSOLUTE in device.capabilities
        ):
            abs = device

        if (
            keyboard is None
            and ei.DeviceCapability.KEYBOARD in device.capabilities
        ):
            keyboard = device
        if (
            touchscreen is None
            and ei.DeviceCapability.TOUCH in device.capabilities
        ):
            touchscreen = device

        device.resume()

        read_queue.put("device added")
        return pointer, abs, keyboard, touchscreen

    # execute the tasks

class Interactions:
    """
    Interactions by the user
    """

    def __init__(self, pointer, abs, keyboard, touchscreen):
        """
        ### Arguments

        ### Returns
        """

        self.pointer = pointer
        self.abs = abs
        self.keyboard = keyboard
        self.touchscreen = touchscreen

    def button_down(self):
        """

        """
        pass

    def button_up(self):
        """

        """
        pass

    def key_down(self):
        """

        """
        pass

    def key_up(self):
        pass

    def scroll_up(self):
        """

        """
        pass

    def scroll_down(self):
        """

        """
        pass

    def type(self):
        """

        """
        pass
