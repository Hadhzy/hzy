"""
Build the protocol python modules from the protocol file.
"""
# This project
from hzy.exceptions.base import *  # pylint: disable=wildcard-import

# third party
import xml.etree.ElementTree as ET
import uuid
import struct
from typing import TYPE_CHECKING
from abc import ABC, abstractmethod
import os

if TYPE_CHECKING:
    from xml.etree.ElementTree import Element

__all__ = ["run", "Protocol"]


class Debug:
    """
    A debug class for the protocol parser.
    """


def _make_arg(parent, tag):
    t = tag.get("type")  # the type of the arg # pylint: disable=invalid-name
    c = "Arg" + t.capitalize()  # find the good class # pylint: disable=invalid-name
    return globals()[c](parent, tag)  # -> Arg_TypeHere(parent, tag)


class BasicXmlTag(ABC):
    """
    The basic xml tag class.
    Only used for tags which require looping through the children.
    """

    def __init__(self):
        self.id = uuid.uuid4()  # pylint: disable=C0103

    @abstractmethod
    def _loop(self, parent: "Element"):
        """
        Loop through child elements.
        The parent must be a xml Element
        """

    @abstractmethod
    def __str__(self) -> str:
        return self.__repr__()

    @abstractmethod
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"


class Entry(BasicXmlTag):
    """
    ### Arguments:
        - enum("Enum"): The enum this entry belongs to.
        - entry("Element"): The entry
    ### Returns:
        - None
    """

    def __init__(self, enum: "Enum", entry: "Element") -> None:
        super().__init__()

        self.enum: "Enum" = enum  # the enum this entry belongs to
        assert entry.tag == "entry"

        self.name: str | None = entry.get("name")  # the name of the entry
        self.value: int = int(entry.get("value"))  # the value of the entry
        self.description: Description | None = None  # the description of the entry
        self.summary: str | None = entry.get(
            "summary", None
        )  # the summary of the entry
        self.since: int = int(entry.get("since", 1))  # the version of the entry

        self._loop(entry)

    def _loop(self, entry):  # pylint: disable=arguments-renamed
        for c in entry:  # pylint: disable=invalid-name
            if c.tag == "description":
                self.description = Description(c)  # Description object
                self.summary = self.description.summary  # set the summary

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"


class Event(BasicXmlTag):
    """
    Represents a xml event tag in the protocol file.

    ### Attributes:
        - interface("Interface"): The interface this event belongs to.
        - event("Element"): The event
        - number(int): The number of the event

    ### Returns:
        - None

    """

    def __init__(self, interface: "Interface", event: "Element", number: int) -> None:
        super().__init__()

        self.interface: Interface = interface  # the interface this event belongs to
        assert event.tag == "event", (
            "The event tag must be event current tag is: " + event.tag
        )

        self.name: str | None = event.get("name")  # the name of the event
        self.number: int = number
        self.since: int = int(event.get("since", 1))
        self.args: list[Arg] = []  # the arguments of the event
        self.description: Description | None = None
        self.summary: str | None = None

        self._loop(event)

    def _loop(self, event):  # pylint: disable=arguments-renamed
        for c in event:  # pylint: disable=invalid-name
            if c.tag == "description":
                self.description = Description(c)  # create the description object
                self.summary = self.description.summary  # set the summary
            elif c.tag == "arg":
                self.args.append(_make_arg(self, c))  # fill up the args list

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"


class Enum(BasicXmlTag):  # pylint: disable=too-many-instance-attributes
    """
    Represents a xml enum tag in the protocol file.

    ### Arguments:
        - interface("Interface"): The interface this enum belongs to.
        - enum("Element"): The enum

    ### Returns:
        - None
    """

    def __init__(self, interface: "Interface", enum: "Element") -> None:
        super().__init__()

        self.interface: Interface = interface  # the interface this enum belongs to
        assert enum.tag == "enum"

        self.name: str | None = enum.get("name")  # the name of the enum
        self.since: int = int(enum.get("since", 1))  # the version of the enum
        self.entries: dict[str, Entry] = {}  # the entries of the enum
        self.description: Description | None = None  # the description of the enum
        self.summary: str | None = None  # the summary of the enum

        self._values: dict[str, int] = {}  # get entry by name
        self._names: dict[int, str] = {}  # get entry by value

        self._loop(enum)

    def _loop(self, enum):  # pylint: disable=arguments-renamed
        for c in enum:  # pylint: disable=invalid-name
            if c.tag == "description":
                self.description = Description(c)  # create the description object
                self.summary = self.description.summary  # set the summary

            elif c.tag == "entry":
                e = Entry(self, c)  # create the entry object # pylint: disable=invalid-name
                self.entries[e.name] = e
                self._values[e.name] = e.value
                self._names[e.value] = e.name

    def __getitem__(self, i):
        if isinstance(i, int):
            return self._names[i]

        return self._values[i]

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"

    def __str__(self) -> str:
        return self.__repr__()


class Arg(BasicXmlTag):
    """
    Represents a xml arg tag in the protocol file.
    """

    def __init__(self, parent, arg):
        super().__init__()

        self.parent = parent  # the parent request
        self.name = arg.get("name")  # the name of the arg
        self.type = arg.get("type")  # the type of the arg

        self.description = None
        self.summary = arg.get("summary", None)
        self.allow_null = arg.get("allow-null", "false") == "true"

        self._loop(arg)

    def _loop(self, arg):  # pylint: disable=arguments-renamed
        for c in arg:  # pylint: disable=invalid-name
            if c.tag == "description":
                self.description = Description(c)
                self.summary = self.description.summary

    def marshal(self, args):
        """
        Marshal the argument.

        Implement this when marshalling for requests and events is the
        same operation.

        args is the list of arguments still to marshal; this call
        removes the appropriate number of items from args.

        The return value is a tuple of (bytes, optional return value,
        list of fds to send).
        """

        raise NotImplementedError

    def unmarshal(self, argdata, fd_source):
        """Unmarshal the argument.

        Implement this when unmarshalling from requests and events is
        the same operation.

        argdata is a file-like object providing access to the
        remaining marshalled arguments; this call will consume the
        appropriate number of bytes from this source

        fd_source is an iterator object supplying fds that have been
        received over the connection

        The return value is the value of the argument.
        """

        raise NotImplementedError

    def marshal_for_request(self, args, proxy):
        """Marshal the argument

        args is the list of arguments still to marshal; this call
        removes the appropriate number of items from args

        proxy is the interface proxy class instance being used for the
        call.

        The return value is a tuple of (bytes, optional return value,
        list of fds to send)
        """

        return self.marshal(args)

    def unmarshal_for_request(self, argdata, fd_source, proxy):
        """Unmarshal the argument.

        argdata is a file-like object providing access to the
        remaining marshalled arguments; this call will consume the
        appropriate number of bytes from this source

        fd_source is an iterator object supplying fds that have been
        received over the connection

        proxy is the interface proxy class instance being used for the
        call.

        The return value is the value of the argument.
        """

        return self.unmarshal(argdata, fd_source)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"

    def __str__(self) -> str:
        return self.__repr__()


class ArgInt(Arg):
    """Signed 32-bit integer argument"""

    def marshal(self, args):
        v = args.pop(0)
        return struct.pack("i", v), None, []

    def unmarshal(self, argdata, fd_source):
        (v,) = struct.unpack("i", argdata.read(4))
        return v


class ArgUint(Arg):
    """Unsigned 32-bit integer argument"""

    def marshal(self, args):
        v = args.pop(0)
        return struct.pack("I", v), None, []

    def unmarshal(self, argdata, fd_source):
        (v,) = struct.unpack("I", argdata.read(4))
        return v


class ArgNewId(Arg):
    """Newly created object argument"""

    def __init__(self, parent, arg):
        super(ArgNewId, self).__init__(parent, arg)
        self.interface = arg.get("interface", None)
        if isinstance(parent, Event):
            assert self.interface

    def marshal_for_request(self, args, proxy):
        nid = proxy.display._get_new_oid()
        if self.interface:
            # The interface type is part of the argument, and the
            # version of the newly created object is the same as the
            # version of the proxy.
            npc = self.parent.interface.protocol[self.interface].client_proxy_class
            version = proxy.version
            b = struct.pack("I", nid)
        else:
            # The interface and version are supplied by the caller,
            # and the argument is marshalled as string,uint32,uint32
            interface = args.pop(0)
            version = args.pop(0)
            npc = interface.client_proxy_class
            iname = interface.name.encode("utf-8")
            parts = (
                struct.pack("I", len(iname) + 1),
                iname,
                b"\x00" * (4 - (len(iname) % 4)),
                struct.pack("II", version, nid),
            )
            b = b"".join(parts)
        new_proxy = npc(proxy.display, nid, proxy.display._default_queue, version)
        proxy.display.objects[nid] = new_proxy
        return b, new_proxy, []

    def unmarshal_from_event(self, argdata, fd_source, proxy):
        assert self.interface
        (nid,) = struct.unpack("I", argdata.read(4))
        npc = self.parent.interface.protocol[self.interface].client_proxy_class
        new_proxy = npc(proxy.display, nid, proxy.display._default_queue, proxy.version)
        proxy.display.objects[nid] = new_proxy
        return new_proxy


class ArgString(Arg):
    """String argument"""

    def marshal(self, args):
        estr = args.pop(0).encode("utf-8")
        parts = (struct.pack("I", len(estr) + 1), estr, b"\x00" * (4 - (len(estr) % 4)))
        return b"".join(parts), None, []

    def unmarshal(self, argdata, fd_source):
        # The length includes the terminating null byte
        (l,) = struct.unpack("I", argdata.read(4))
        assert l > 0
        l = l - 1
        s = argdata.read(l).decode("utf-8")
        argdata.read(4 - (l % 4))
        return s


class ArgObject(Arg):
    """Existing object argument"""

    def marshal(self, args):
        v = args.pop(0)
        if v:
            oid = v.oid
        else:
            if self.allow_null:
                oid = 0
            else:
                raise HzyNullException("Null object not allowed")
        return struct.pack("I", oid), None, []

    def unmarshal_from_event(self, argdata, fd_source, proxy):
        (v,) = struct.unpack("I", argdata.read(4))
        return proxy.display.objects.get(v, None)


class ArgFd(Arg):
    """File descriptor argument"""

    def marshal(self, args):
        v = args.pop(0)
        fd = os.dup(v)
        return b"", None, [fd]

    def unmarshal(self, argdata, fd_source):
        return fd_source.pop(0)


class ArgFixed(Arg):
    """Signed 24.8 decimal number argument"""

    # particular, is it (as the protocol description says) a sign bit
    # followed by 23 bits of integer precision and 8 bits of decimal
    # precision, or is it 24 bits of 2's complement integer precision
    # followed by 8 bits of decimal precision?  I've assumed the
    # latter because it seems to work!

    def marshal(self, args):
        v = args.pop(0)
        if isinstance(v, int):
            m = v << 8
        else:
            m = (int(v) << 8) + int((v % 1.0) * 256)
        return struct.pack("i", m), None, []

    def unmarshal(self, argdata, fd_source):
        b = argdata.read(4)
        (m,) = struct.unpack("i", b)
        return float(m >> 8) + ((m & 0xFF) / 256.0)


class ArgArray(Arg):
    """Array argument"""

    # This appears to be very similar to a string, except without any
    # zero termination.  Interpretation of the contents of the array
    # is request- or event-dependent.

    def marshal(self, args):
        v = args.pop(0)
        # v should be bytes
        parts = (struct.pack("I", len(v)), v, b"\x00" * (3 - ((len(v) - 1) % 4)))
        return b"".join(parts), None, []

    def unmarshal(self, argdata, fd_source):
        (l,) = struct.unpack("I", argdata.read(4))
        v = argdata.read(l)
        pad = 3 - ((l - 1) % 4)
        if pad:
            argdata.read(pad)
        return v


class Request(BasicXmlTag):
    """
    Represent a xml request tag, and a request on an interface.
    Requests have a name, optional type(to indicate whether the request destroys the object),

    ### Arguments:
        - interface("Interface"): The interface the request belongs to.
        - opcode(int): The opcode of the request. (it's not defined in the protocol xml)
        - request("Element"): The xml request tag.

    ### Returns:
        - None
    """

    def __init__(
        self, interface: "Interface", opcode: int | None, request: "Element"
    ) -> None:
        super().__init__()

        self.interface: Interface = interface  # the interface this request belongs to
        self.opcode: int | None = opcode  # not defined in the protocol xml
        assert request.tag == "request", (
            "The request tag must be request current tag is: " + request.tag
        )

        self.name: str | None = request.get("name")  # the name of the request
        self.type: str | None = request.get("type")  # the type of the request
        self.since: int = int(
            request.get("since")
        )  # the version of the protocol when it was added

        self.is_destructor: bool = (
            self.type == "destructor"
        )  # true if the request is a destructor

        self.description: Description | None = None  #
        self.summary: str | None = None
        # if the interface creates a new object, this is the interface of the new object
        self.creates: Interface | None = None

        self.args: list[Arg] = []  # store the arguments of the request

        self._loop(request)

    def _loop(self, request):
        for c in request:
            if c.tag == "description":
                # the description of the request
                self.description = Description(c)  # fill the description
                self.summary = self.description.summary  # fill up the summary

            elif c.tag == "arg":
                # an arg inside a request
                a = _make_arg(self, c)  # make the arg object, find the type of the arg
                if a.type == "new_id":
                    # if the arg is a new_id, the request creates a new object
                    self.creates = a.interface

                self.args.append(a)  # add the arg to the args list

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
            # the proxy destroyed there is nothing to do
            return

        if proxy.version < self.since:
            raise HzyProxyTooOld("The proxy version is too old.", "request version: ")

        r = proxy._marshal_request(self, *args)

        if self.is_destructor:
            proxy.destroyed = True

        return r

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"

    def __str__(self) -> str:
        return self.__repr__()


class Description(BasicXmlTag):
    """
    Represents a description tag in the protocol system.
    """

    def __init__(self, interface) -> None:
        super().__init__()

        self.description = interface.get("description")  # the description
        self.summary: str = self.description.attrib[
            "summary"
        ]  # summary from the description

    def __repr__(self) -> str:
        return f"<Description summary={self.summary} id={self.id}>"

    def __str__(self) -> str:
        return self.__repr__()

    def _loop(self, parent: "Element"):
        """
        not needed in the description tag
        """


class Interface(BasicXmlTag):
    """
    Represents an interface in the protocol system.

    ### Arguments:
        - interface: The xml interface to parse.

    ### Returns:
        - None
    """

    # implements slots to save memory

    def __init__(self, interface: "Element") -> None:
        super().__init__()

        self.interface = interface  # store the xml interface
        assert interface.tag == "interface", (
            "The interface tag must be interface current tag is: " + interface.tag
        )

        self.name = interface.get("name")  # interface name
        self.version: int = int(interface.get("version"))  # interface version

        self.description: Description | None = None  # description of the interface
        self.summary: str | None = None
        self.requests: list[Request] | dict = {}
        self.events_by_name: dict[str, Event] = {}  # get event by name
        self.events_by_number: list[Event] = []  # get event by number
        self.enums: dict[str, Enum] = {}

        self._loop(interface)  # start searching for tags

    def _loop(self, interface):
        for c in interface:
            if c.tag == "description":
                self.description = Description(c)
                self.summary = self.description.summary

            elif c.tag == "request":
                e = Request(self, len(self.requests), c)  # interface, opcode, request
                self.requests[e.name] = c

            elif c.tag == "event":
                e = Event(self, c, len(self.events_by_number))
                self.events_by_name[e.name] = e
                self.events_by_number.append(e)

            elif c.tag == "enum":
                e = Enum(self, c)
                self.enums[e.name] = e

    def __repr__(self) -> str:
        return f"<Interface name={self.name} version={self.version} description=<{Description}> > "

    def __str__(self):
        return self.__repr__()


class Protocol:
    """
    The Entry point.
    Represents the libei protocol.
    Stores all of the interfaces.

    ### Arguments:
        - protocol_file: The path to the protocol file.

    ### Returns:
        - None
    """

    VERSION = "1.0"  # hzy protocol version
    INTERFACES: list[Interface] = []  # strores all the interfaces

    class Meta:
        """
        The metadata of the protocol(libei)
        The data is coming from the provided protocol file.
        """

        def __init__(self) -> None:
            self.version: str | None = None  # libei protocol version
            self.name = None  # libei protocol name
            self.copy_right = None  # libei protocol copy right

    def __init__(self, protocol_file=None) -> None:
        self.tree = ET.parse(protocol_file)  # parse the protocol file
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

        self.meta.version = Protocol.VERSION  # # get the version from the protocol file

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
    Run the protocol file and generate cache.

    ### Arguments:
        - protocol_file: The path to the protocol file.
        - long_description: Whether to print the long description or not.

    ### Returns:
        -None | str
    """

    protocol = Protocol(protocol_file=protocol_file)

    if long_description:
        return protocol.__str__()

    return None


if __name__ == "__main__":
    out = run("protocol.xml")
