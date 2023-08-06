import select

__all__ = ["wait_for_portal"]
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

