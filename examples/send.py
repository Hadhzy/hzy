from hzy import *

"""
Send a button down event to the desktop with basic config
"""

desktop = Desktop.send()

desktop.interact.button_down(KEY_ENTER)
