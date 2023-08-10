import snegg.ei as ei
from snegg.eis import EventType
from snegg.ei import EventType as ei_event_type
from typing import TYPE_CHECKING

# This project
from hzy.client import Client
import hzy.event as event
from hzy.utils import adder

if TYPE_CHECKING:
    from queue import Queue


def handle_request(event, read_queue: Queue):
    """
    (source: https://gitlab.freedesktop.org/libinput/snegg/-/blob/main/examples/eis-demo-server.py)
    ### Arguments

    ### Returns

    """

    pointer = None
    abs = None
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

        if pointer is None and ei.DeviceCapability.POINTER in device.capabilities:
            pointer = device

        if abs is None and ei.DeviceCapability.POINTER_ABSOLUTE in device.capabilities:
            abs = device

        if keyboard is None and ei.DeviceCapability.KEYBOARD in device.capabilities:
            keyboard = device
        if touchscreen is None and ei.DeviceCapability.TOUCH in device.capabilities:
            touchscreen = device

        device.resume()

        read_queue.put("device added")
        return pointer, abs, keyboard, touchscreen

    # execute the tasks


class Interactions:
    """
    Interactions by the user
    """

    def __init__(self):
        """
        ### Arguments

        ### Returns
        """

        self.pointer = None
        self.abs = None
        self.keyboard = None
        self.touchscreen = None

    def add_devices(self, pointer, abs, keyboard, touchscreen) -> None:
        """
        ### Arguments
            - pointer: ei.Device - The pointer device
            - abs: ei.Device - The absolute device
            - keyboard: ei.Device - The keyboard device
            - touchscreen: ei.Device - The touchscreen device
        ### Returns
            - None
        """

        self.pointer = pointer
        self.abs = abs
        self.keyboard = keyboard
        self.touchscreen = touchscreen

    @adder(data_path=event.STORED)
    def move_cursor(self, x: int, y: int, abs=True) -> None:
        """
        ### Arguments
            - x: int - The x coordinate to move to
            - y: int - The y coordinate to move to
            - abs: bool - Whether to use absolute coordinates or not
        ### Returns
            - None
        """

        if abs:
            self.abs.start_emulating().pointer_motion_absolute(x, y).stop_emulating()

        else:
            self.pointer.start_emulating().pointer_motion(x, y).stop_emulating()

    @adder(data_path=event.STORED)
    def button_down(self, button: int, is_press: bool = True) -> None:
        """
        ### Arguments
            - button: int - The button to press(linux/input-event-codes.h)
            - is_press: bool - Whether to press or release the button
        ### Returns
            - None
        """

        self.pointer.start_emulating().button_button(button, is_press).stop_emulating()

    @adder(data_path=event.STORED)
    def button_up(self, button: int, is_press: bool = False) -> None:
        """
        ### Arguments
            - button: int - The button to press(from linux/input-event-codes.h)
            - is_press: bool - Whether to press or release the button
        ### Returns
            - None
        """

        self.pointer.start_emulating().button_button(button, is_press).stop_emulating()

    @adder(data_path=event.STORED)
    def key_down(self, key: int, is_press: bool = True) -> None:
        """
        ### Arguments
            key: int - The key to press
            is_press: bool - Whether to press or release the key(True = press, False = release
        ### Returns
            - None
        """

        self.keyboard.start_emulating().keyboard_key(key, is_press).stop_emulating()

    @adder(data_path=event.STORED)
    def key_up(self, key: int, is_press: bool = False) -> None:
        """
        ### Arguments
            key: int - The key to press
            is_press: bool - Whether to press or release the key(True = press, False = release)

        ### Returns
            - None
        """

        self.keyboard.start_emulating().keyboard_key(key, is_press).stop_emulating()

    @adder(data_path=event.STORED)
    def scroll(self, clicks: int = 1) -> None:
        """
        ### Arguments
            - clicks: int - The number of clicks to scroll
        ### Returns
            - None
        """
        clicks = clicks * 120

        self.pointer.start_emulating().scroll_discrete_event(clicks).stop_emulating()
