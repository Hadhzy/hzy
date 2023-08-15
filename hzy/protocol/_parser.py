"""
Build the protocol python modules from the protocol file.
"""

# Todo: Add debug feature

# third party
import xml.etree.ElementTree as ET
import uuid
from typing import TYPE_CHECKING
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    from xml.etree.ElementTree import Element

# This project
from hzy.exceptions.base import HzyDeletedProxy

__all__ = ["run", "Protocol"]


class BasicXmlTag(ABC):
    """
    The basic xml tag class.
    Only used for tags which require looping through the children.
    """

    @abstractmethod
    def _loop(self, parent: "Element"):
        pass

    @abstractmethod
    def __str__(self) -> str:
        return self.__repr__()

    @abstractmethod
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"


class Event(BasicXmlTag):
    def _loop(self, parent):
        pass

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"


class Enum(BasicXmlTag):
    def _loop(self, parent):
        pass

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"

    def __str__(self) -> str:
        return self.__repr__()


class Arg(BasicXmlTag):
    def _loop(self, parent):
        pass

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"

    def __str__(self) -> str:
        return self.__repr__()


class Request(BasicXmlTag):
    """
    A request on an interface.
    Requests have a name, optional type(to indicate whether the request destroys the object),

    ### Arguments:
        - None

    ### Returns:
        - None
    """

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"

    def __str__(self) -> str:
        return self.__repr__()

    def __init__(self, interface: "Interface", opcode: int, request: "Element") -> None:
        self.interface = interface
        self.opcode = opcode
        assert request.tag == "request", (
            "The request tag must be request current tag is: " + request.tag
        )

        self.name = request.get("name")
        self.type = request.get("type")
        self.since = int(request.get("since"))

        self.is_destructor = self.type == "destructor"

        self.description = None
        self.summary = None
        self.creates = None

        self.args = None

        self._loop(request)

    def _loop(self, request):
        for c in request:
            if c.tag == "description":
                self.description = Description(c)
                self.summary = self.description.summary
            # Todo: Define arg
            # elif c.tag == "arg":
            #     a = Arg(self, c)
            #     if a.type == "new_id":
            #         self.creates = a.interface
            #
            #     self.args.append(a)

    def invoke(self, proxy, *args):
        """
        Invoke the request on a client proxy.

        ### Arguments:
            proxy: The client proxy to invoke the request on.
            *args: The arguments to pass to the request.
        ### Returns:
            - None
        """

        if not proxy.oid:
            raise HzyDeletedProxy("The proxy is deleted.")

        if proxy.destroyed:
            return

        if proxy.version < self.since:
            raise Exception("The proxy version is too old.", "request version: ")

        r = proxy._marshal_request(self, *args)

        if self.is_destructor:
            proxy.destroyed = True

        return r


class Description:
    """
    Represents a description in the protocol system.
    """

    def __init__(self, interface) -> None:
        self.description = interface.get("description")  # xml description
        self.summary: str = self.description.attrib[
            "summary"
        ]  # summary from the description
        self.id = uuid.uuid4()  # generate a unique id for the description

    def __repr__(self) -> str:
        return f"<Description summary={self.summary} id={self.id}>"

    def __str__(self) -> str:
        return self.__repr__()


class Interface:
    """
    Represents an interface in the protocol system.

    ### Arguments:
        - interface: The xml interface to parse.

    ### Returns:
        - None
    """

    def __init__(self, interface) -> None:
        self.interface = interface  # xml interface
        assert interface.tag == "interface", (
            "The interface tag must be interface current tag is: " + interface.tag
        )

        self.name = interface.get("name")  # interface name
        self.version: int = int(interface.get("version"))  # interface version

        self.description: Description | None = None  # description of the interface
        self.summary: str | None = None
        self.requests: list[Request] | dict = {}
        self.events_by_name = {}
        self.events_by_number = []
        self.enums = {}

        self._loop(interface)  # start searching for tags

    def _loop(self, interface):
        for c in interface:
            if c.tag == "description":
                self.description = Description(c)
                self.summary = self.description.summary

            elif c.tag == "request":
                e = Request(self, len(self.requests), c)  # interface, opcode, request
                self.requests[e.name] = c

            # Todo: define event
            elif c.tag == "event":
                self.events_by_name[c.get("name")] = c
                self.events_by_number.append(c)

            # Todo: define enum
            elif c.tag == "enum":
                self.enums[c.get("name")] = c

    def __repr__(self) -> str:
        return f"<Interface name={self.name} version={self.version} description=<{Description}> > "

    def __str__(self):
        return self.__repr__()


class Protocol:
    """
    The Entry point.
    Represents the libei protocol.

    ### Arguments:
        - protocol_file: The path to the protocol file.

    ### Returns:
        - None
    """

    VERSION = "1.0"  # hzy protocol version
    INTERFACES = []  # strores all the interfaces

    class Meta:
        """
        The metadata of the protocol(libei)
        The data is coming from the provided protocol file.
        """

        def __init__(self):
            self.version = None  # libei protocol version
            self.name = None  # libei protocol name
            self.copy_right = None  # libei protocol copy right

    def __init__(self, protocol_file=None) -> None:
        self.tree = ET.parse(protocol_file)
        root = self.tree.getroot()  # get the root element of the protocol file

        self.meta = self._setup_meta(root)  # fill up the metadata
        self.generate(root)  # fill up the interfaces

    def _setup_meta(self, root) -> Meta:
        self.meta = self.Meta()  # initialise the metaobject

        self.meta.name = root.attrib["name"]  # set the name of the protocol

        for child in root:
            if child.tag == "copyright":
                self.meta.copy_right = child.text
                break

        self.meta.version = (
            Protocol.VERSION
        )  # Todo: get the version from the protocol file

        return self.meta

    def generate(self, root: "Element") -> None:
        """
        Start the process by invoking interface classes

        ### Arguments:
            - root: The root element of the protocol file.

        ### Returns:
            - None
        """

        for child in root:
            if child.tag == "interface":
                self.INTERFACES.append(Interface(child))

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self):
        return (
            f"<Hzy version={self.VERSION}> <Meta version={self.meta.version} name={self.meta.name} "
            f"copy_right={self.meta.copy_right}>"
        )


def run(protocol_file="protocol.xml", long_description=False) -> None | str:
    """
    Build the protocol python modules from the protocol file.

    ### Arguments:
        - protocol_file: The path to the protocol file.
        - long_description: Whether to print the long description or not.(protocol.repr or protocol.str)

    ### Returns:
        -None | str
    """

    protocol = Protocol(protocol_file=protocol_file)

    if long_description:
        return protocol.__str__()


if __name__ == "__main__":
    out = run("protocol.xml")
