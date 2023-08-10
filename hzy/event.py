import select
from queue import Queue
import snegg.ei as ei
from snegg.eis import EventType
from snegg.ei import EventType as ei_event_type
from typing import Type

# This project
from hzy.utils import execute_them
from hzy.client import Client
from hzy.utils import ConfigEvents, ConfigRequest

STORED = []  # tasks to execute


def handle_request(event, read_queue: "Queue"):
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


class Event:
    """
    Handles events

    ### Arguments
        - ctx: ei.Receiver | ei.Sender - The context to use
        - interested_in: list | str - The events to listen to(NOTE: if you want to listen to all events, pass "all",
        otherwise pass a list of events type)
        - get_there: callable - The function to call when the event is received

    ### Returns
        - None
    """

    def __init__(self, config: Type[ConfigEvents] | Type[ConfigRequest]) -> None:
        self.config = config

        self.ctx = self.config.CTX

        self.device_ready = Queue()

        if self.ctx is ei.Sender:
            self.config.GET_THERE = handle_request

        self.get_there = self.config.GET_THERE
        self.interested_in = self.config.INTERESTED_IN

        self._start_loop()

    def _start_loop(self):
        print("ctx", self.ctx)
        print("fd: ", self.ctx.fd)
        poll = select.poll()
        poll.register(self.ctx.fd)

        result = None

        while poll.poll():
            self.ctx.dispatch()

            for e in self.ctx.events:
                if self.interested_in == "all":
                    result = self.get_there(e, self.device_ready)

                if self.interested_in is not "all" and type(self.interested_in) is list:
                    if e.event_type in self.interested_in:
                        result = self.get_there(e, self.device_ready)

                if self.device_ready.get() == "device added":
                    # execute the tasks pass in devices

                    assert result is not None

                    pointer, abs, keyboard, touch = result

                    for _item in STORED:
                        execute_them(_item, pointer, abs, keyboard, touch)

                    # Finished executing the tasks
                    break
