import select
import dataclasses
from typing import Any
import snegg.ei as ei


@dataclasses.dataclass
class ConfigEvents:
    """
    Configure Events(receiver)
    """
    INTERESTED_IN: Any = "all"
    GET_THERE: callable = None
    CTX: ei.Receiver | ei.Sender = ei.Receiver

@dataclasses.dataclass
class CONFIG:
    """
    Represents basic configuration for the desktop
    """
    SOCKET_NAME: str = None
    SOCKET_PATH: str = None


@dataclasses.dataclass
class ConfigRequest(ConfigEvents):
    """
    Configure requests(sender)
    """
    INTERESTED_IN = ["request"]
    CTX: ei.Receiver | ei.Sender = ei.Sender

def wait_for_portal():
    import snegg.oeffis

    portal = snegg.oeffis.Oeffis.create()

    poll = select.poll()
    poll.register(portal.fd)
    while poll.poll():
        try:
            if portal.dispatch():
                # We need to keep the portal object alive, so we don't get disconnected
                return portal
        except snegg.oeffis.SessionClosedError as e:
            print(f"Closed: {e}", e.message)
            raise SystemExit(1)
        except snegg.oeffis.DisconnectedError as e:
            print(f"Disconnected: {e}", e.message)
            raise SystemExit(1)


def select_config_files(config: list, default_configs):
    """
    Returns the config files

    ### Arguments
        - config:list - The config to use(user specified)
        - default_configs:list - The default configs to use(specified above)
    ### Returns
        - list - list of config types
        [0] -> CONFIG
        [1] -> ConfigEvents
        [2] -> ConfigRequest
    """
    configs = []
    _count = 0
    for conf in config:

        if conf is isinstance(conf, (CONFIG, ConfigEvents, ConfigRequest)):
            configs.append(conf)

        else:
             configs.append(default_configs[_count])

        _count += 1

    return configs