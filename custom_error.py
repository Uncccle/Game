class IncorrectConfigurations(Exception):
    def __init__(self, message):
        self._message = message
    def __str__(self):
        return repr(self._message)