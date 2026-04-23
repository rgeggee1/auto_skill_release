# hotkey.py

# Define your hotkey functionalities here

class HotkeyManager:
    def __init__(self):
        self.hotkeys = {}

    def add_hotkey(self, key, action):
        self.hotkeys[key] = action

    def remove_hotkey(self, key):
        if key in self.hotkeys:
            del self.hotkeys[key]

    def execute_action(self, key):
        if key in self.hotkeys:
            self.hotkeys[key]()

# Example usage:
# def example_action():
#     print("Hotkey activated!")
# 
hm = HotkeyManager()
# hm.add_hotkey('ctrl+h', example_action)