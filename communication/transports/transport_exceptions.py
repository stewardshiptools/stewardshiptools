# class ValidationError(Exception):
#     def __init__(self, message, errors):
#
#         # Call the base class constructor with the parameters it needs
#         super(ValidationError, self).__init__(message)
#
#         # Now for your custom code...
#         self.errors = errors


class TransportException(Exception):
    pass


class LoginError(TransportException):
    pass


class ConnectionError(TransportException):
    pass


class OAuth2ConnectionError(TransportException):
    pass


class TimeoutError(TransportException):
    pass
