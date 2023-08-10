import hzy.utils as utils
import snegg.ei as ei
from typing import Type, Any

_type_cls = Type[ei.Receiver] | Type[ei.Sender]
# This project
from hzy.event import Event
from hzy.request import Interactions

CONFIG_TYPES = (
    utils.ConfigEvents | utils.ConfigRequest | utils.CONFIG
)  # represents the types of the config
default_configs = [
    utils.CONFIG,
    utils.ConfigEvents,
    utils.ConfigRequest,
]  # default configs to use


class Desktop:
    """
    Represents the desktop of the user.
    ### Arguments
        - use_portal:bool - Whether to use the portal or not
        - cls:ei.Receiver | ei.Sender -  The class to use(Receiver or Sender) -> for the first time
        - config:CONFIG - The configuration to use

    ### Returns
        - None

    """

    def __init__(
        self,
        use_portal: bool = True,
        cls: _type_cls = ei.Receiver,
        config: list[CONFIG_TYPES] | Any = None,
    ):
        self._cls = cls  # sender or receiver

        self.interact = Interactions()  # the interactions object

        _config, config_events, config_request = utils.select_config_files(
            config, default_configs
        )

        if isinstance(self._cls, ei.Receiver):
            self.event = Event(config_events)

        elif isinstance(self._cls, ei.Sender):
            self.request = Event(config_request)

        else:
            raise TypeError(
                "cls must be a Sender or Receiver, currently it is ", self._cls
            )

        self._ctx = self._use_portal(use_portal, cls, _config)

    # noinspection PyMethodMayBeStatic
    def _use_portal(self, use_portal, cls, config: Any):
        """
        Use the portal
        ### Arguments
            - use_portal:bool - Whether to use the portal or not
            - cls:ei.Receiver | ei.Sender -  The class to use(Receiver or Sender) -> for the first time
            - config:CONFIG - The configuration to use

        ### Returns
            - "EIS"

        """

        if use_portal:
            portal = utils.wait_for_portal()

            assert portal is not None

            return cls.create_for_fd(portal.eis_fd, name=config.SOCKET_NAME)

        return cls.create_for_socket(path=config.SOCKET_PATH, name=config.SOCKET_NAME)

    @classmethod
    def send(cls, *args, **kwargs):
        """
        Send a request to the server
        ### Arguments

        ### Returns

        """

        use_portal = kwargs.get("use_portal", True) or args[0]
        _cls = kwargs.get("cls", ei.Sender) or args[1]
        _config = kwargs.get("config", default_configs) or args[2]

        return cls(use_portal=use_portal, cls=_cls, config=_config)

    @classmethod
    def receive(cls, *args, **kwargs):
        """
        Receive a request from the server
        ### Arguments
            - use_portal:bool - Whether to use the portal or not
            - cls:ei.Receiver | ei.Sender -  The class to use(Receiver or Sender) -> for the first time
            - config:CONFIG - The configuration to use
        ### Returns

        """

        use_portal = kwargs.get("use_portal", True) or args[0]
        _cls = kwargs.get("cls", ei.Receiver) or args[1]
        _config = kwargs.get("config", default_configs or args[2])

        return cls(use_portal=use_portal, cls=_cls, config=_config)
