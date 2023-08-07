import select
from typing import TYPE_CHECKING
import snegg.ei as ei
from queue import Queue

if TYPE_CHECKING:
    from utils import ConfigEvents, ConfigRequest
    from typing import Type

# This project
from hzy.request import handle_request
from hzy.utils import execute_them

STORED = []  # tasks to execute


class Event:
    """
    Handles events

    ### Arguments
        - ctx: ei.Receiver | ei.Sender - The context to use
        - interested_in: list | str - The events to listen to(NOTE: if you want to listen to all events, pass "all", otherwise pass a list of events type)
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