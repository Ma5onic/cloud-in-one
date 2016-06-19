
class RetryException(Exception):
    """This exception means that you should retry the last action"""
    pass


class FullStorageException(Exception):
    """This exception means that the storage quota is full"""
    pass


class APILimitedException(Exception):
    """This exception means that you used the API too much"""
    pass


class UnknownError(Exception):
    """This exception is generic. We don't know what happened"""
    pass


class SecurityError(Exception):
    """Unrecoverable security breach"""
    pass
