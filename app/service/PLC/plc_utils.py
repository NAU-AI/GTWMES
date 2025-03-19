import functools

from utility.logger import Logger

logger = Logger.get_logger(__name__)


def require_connection(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self.is_connected():
            logger.error("PLC is not connected. Cannot execute %s.", func.__name__)
            return None
        return func(self, *args, **kwargs)

    return wrapper
