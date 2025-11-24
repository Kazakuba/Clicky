import json

class Settings:
    def __init__(self):
        self.run_in_background = False
        self.auto_load_last_workflow = True
        self.theme = "Default"

    def save(self, filepath):
        with open(filepath, 'w') as f:
            json.dump(self.__dict__, f)

    def load(self, filepath):
        try:
            with open(filepath, 'r') as f:
                self.__dict__.update(json.load(f))
        except FileNotFoundError:
            pass