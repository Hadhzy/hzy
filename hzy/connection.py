import dataclasses

@dataclasses.dataclass
class Connection:
    state = False # not connected by default

    def __repr__(self):
        return self.__str__()

    def __str__(self):

        _value = "connected" if self.state else "not connected"

        return f"Connection(state={_value})"