"""
Basic connection to the unix socket.
Every client has a connection to the unix socket.
Every connection has a unique id.
Every connection has a state.
Every connection has a client.
"""

import socket
import uuid
import os
__all__ = ["Connection", ]


class _State:
    CONNECTED = "CONNECTED"
    DISCONNECTED = "DISCONNECTED"


class Connection:
    """
    Represents a connection to the unix socket.
    """
    def __init__(self, client):
        self.client = client  # the client that the connection is for.
        self.id = uuid.uuid4()  # generate a unique id for the connection.
        self.state = _State.DISCONNECTED  # set the state to disconnected.
        self._connect()  # call the connect method to connect to the unix socket.

    def __repr__(self) -> str:
        return f"<Connection id={self.id} client={self.client}>"

    def __str__(self) -> str:
        return self.__repr__()

    # noinspection PyMethodMayBeStatic
    def to_server(self) -> str:
        return "to server"

    # noinspection PyMethodMayBeStatic
    def _connect(self):
        host = ""
        port = ""
        env_socket_path = os.getenv["LIBEI_SOCKET"]

        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
            s.bind((host, port))
            s.listen()
            conn, addr = s.accept()

            with conn:
                self.state = _State.CONNECTED  # set the state to connected.
                while True:
                    data = conn.recv(1024)  # receive data from the server

                    self.client.set_data(data)  # send the data to the client

                    if not data:
                        break

                    conn.sendall(self.to_server())
                    # send the data to the server
