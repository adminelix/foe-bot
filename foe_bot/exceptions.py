class RequestException(Exception):
    def __init__(self, message):
        super().__init__(message)


class ResponseException(Exception):
    def __init__(self, message):
        super().__init__(message)


class WrongCredentialsException(Exception):
    def __init__(self, message):
        super().__init__(message)


class WorldNotFoundException(Exception):
    def __init__(self, message):
        super().__init__(message)
