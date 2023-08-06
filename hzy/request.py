from snegg.eis import Eis, EventType, DeviceCapability
def handle_request(event):
    """
    (source: https://gitlab.freedesktop.org/libinput/snegg/-/blob/main/examples/eis-demo-server.py)
    :param event:
    :return:
    """
    if event.event_type == EventType.CLIENT_CONNECT:
        client = event.client
        client.connect()

        # create the seat
        seat = client.new_seat()
        seat.add()

    elif event.event_type == EventType.SEAT_BIND:
        seat = event.seat
        assert seat is not None

        caps = event.seat_event.capabilities

        if DeviceCapability.POINTER in caps:
            device = seat.new_device(

            )

            device.add()
            device.resume()

        if DeviceCapability.KEYBOARD in caps:
            device = seat.new_device(
                name="keyboard device", capabilities=[DeviceCapability.KEYBOARD]
            )
            device.add()
            device.resume()
