from hzy import *

"""
Receive every event and invoke execute_me when an event occurs
"""

def execute_me(event):
    print("Hello World!")

custom_config = ConfigEvents(GET_THERE=execute_me)

desktop = Desktop.receive(config=custom_config)



