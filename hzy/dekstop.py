from utils import *
import snegg.ei as ei
import dataclasses
from typing import Type
_type_cls = Type[ei.Receiver] | Type[ei.Sender]

@dataclasses.dataclass
class CONFIG:
    """
    Represents basic configuration for the desktop
    """
    SOCKET_NAME: str = None
    SOCKET_PATH: str = None

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

    def __init__(self, use_portal: bool = True, cls:_type_cls = ei.Receiver, config: CONFIG = None):
        self.cls = cls # sender or receiver
        self.ctx = self._use_portal(use_portal, cls, config)

    #noinspection PyMethodMayBeStatic
    def _use_portal(self, use_portal, cls, config):
        """
        Use the portal
        :param use_portal:
        :return:
        """

        if use_portal:
            portal = wait_for_portal()

            assert portal is not None

            return cls.create_for_fd(portal.eis_fd, name=config.SOCKET_NAME)

        return cls.create_for_socket(path=config.SOCKET_PATH, name=config.SOCKET_NAME)

    def _setup(self, use_portal: bool = True):
        pass

    @classmethod
    def send(cls, *args, **kwargs):
        """
        Send a request to the server
        :return:
        """
        use_portal = kwargs.get("use_portal", True) or args[0]
        _cls = kwargs.get("cls", ei.Sender) or args[1]
        _config = kwargs.get("config", None) or args[2]

        return cls(use_portal=use_portal, cls=_cls, config=_config)

    @classmethod
    def receive(cls, *args, **kwargs):
        """
        Receive a request from the server
        :return:
        """

        use_portal = kwargs.get("use_portal", True) or args[0]
        _cls = kwargs.get("cls", ei.Receiver) or args[1]
        _config = kwargs.get("config", None) or args[2]

        return cls(use_portal=use_portal, cls=_cls, config=_config)
