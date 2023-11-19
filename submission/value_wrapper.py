class ValueWrapper:
    def __init__(self, value):
        self.value = value

    def get_val(self):
        return self.value

    def set_value(self, value):
        self.value = value

    def evaluate(self):
        return self
