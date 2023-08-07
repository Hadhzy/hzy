from hzy import *

def execute_me(event):
    print("Hello World!")

custom_config = ConfigEvents(GET_THERE=execute_me)

desktop = Desktop.receive(config=custom_config)



