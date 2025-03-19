class NotFoundException(Exception):
    def __init__(self, message="Resource not found"):
        super().__init__(message)


class ConflictException(Exception):
    def __init__(self, message="Conflict detected"):
        super().__init__(message)


class DatabaseException(Exception):
    def __init__(self, message="Database operation failed"):
        super().__init__(message)


class ServiceException(Exception):
    def __init__(self, message="Service encountered an error"):
        super().__init__(message)
