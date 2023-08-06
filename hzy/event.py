import select
import dataclasses
import snegg.ei as ei
from typing import Any
__all__ = ["Event", "ConfigEvents"]

@dataclasses.dataclass
class ConfigEvents:
    INTERESTED_IN: Any = "all"
    GET_THERE: callable = None
    CTX: ei.Receiver | ei.Sender = ei.Receiver
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

    def __init__(self, config: ConfigEvents) -> None:

        self.interested_in = config.INTERESTED_IN
        self.ctx = config. CTX
        self.get_there = config.GET_THERE

        self._start_loop()

    def _start_loop(self):
        poll = select.poll()
        poll.register(self.ctx.fd)

        while poll.poll():

            self.ctx.dispatch()

            for e in self.ctx.events:

                if self.interested_in == "all":
                    self.get_there(e)

                if self.interested_in is not "all" and type(self.interested_in) is list:

                    if e.event_type in self.interested_in:
                        self.get_there(e)
