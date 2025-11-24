class Action:
    def __init__(self, action_type, **kwargs):
        self.action_type = action_type
        self.params = kwargs

    def to_dict(self):
        return {"action_type": self.action_type, "params": self.params}

    @classmethod
    def from_dict(cls, data):
        return cls(data["action_type"], **data["params"])