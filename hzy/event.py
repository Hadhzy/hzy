import select
from typing import TYPE_CHECKING
import snegg.ei as ei

if TYPE_CHECKING:
    from utils import ConfigEvents, ConfigRequest
    from typing import Type

# This project
from hzy.request import handle_request

ei.libei
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

        if self.ctx is ei.Sender:

            self.config.GET_THERE = handle_request

        self.get_there = self.config.GET_THERE
        self.interested_in = self.config.INTERESTED_IN

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
