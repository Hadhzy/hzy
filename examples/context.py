from hzy import *
from hzy.bindings import ei

"""
Only interested in keyboard events
Invoke func1 when a keyboard event occurs
"""

def func1(event):
    print(event)

config_events = ConfigEvents(INTERESTED_IN=ei.EventType.KEYBOARD_KEY, GET_THERE=func1) # Create a custom config request

desktop = Desktop.send(config_events) # Send the config request

