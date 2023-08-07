import dataclasses


@dataclasses.dataclass
class Connection:
    state = False  # not connected by default

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        _value = "connected" if self.state else "not connected"

        return f"Connection(state={_value})"


class Client:
    """ """

    COUNT = 0  # Count of clients

    def __init__(self, c_obj):
        Client.COUNT += 1
        self.connection = Connection()
        self.c_obj = c_obj
        self.seat_added = False

    def connect(self):
        """

        :return:
        """
        self.connection.state = True
        self.c_obj.connect()

    def new_seat(self):
        """

        :return:
        """
        self.c_obj.new_seat()
        self.seat_added = True
