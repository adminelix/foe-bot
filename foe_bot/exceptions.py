class RequestException(Exception):
    def __init__(self, message):
        self.message = message


class WrongCredentialsException(Exception):
    def __init__(self, message):
        self.message = message


class WorldNotFoundException(Exception):
    def __init__(self, message):
        self.message = message
