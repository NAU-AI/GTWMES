import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)


def get_log_filename():
    return LOG_DIR / f"app.{datetime.now().strftime('%Y-%m-%d')}.log"


class CustomTimedRotatingFileHandler(TimedRotatingFileHandler):
    def __init__(
        self, filename, when="midnight", interval=1, backupCount=7, encoding=None
    ):
        super().__init__(
            filename=str(LOG_DIR / "app.log"),
            when=when,
            interval=interval,
            backupCount=backupCount,
            encoding=encoding,
        )
        self.suffix = "%Y-%m-%d"

    def rotation_filename(self, default_name):
        timestamp = datetime.now().strftime(self.suffix)
        return str(LOG_DIR / f"app.{timestamp}.log")


class Logger:
    _loggers = {}

    @staticmethod
    def get_logger(name):
        if name in Logger._loggers:
            return Logger._loggers[name]

        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        logger.propagate = False

        if not logger.handlers:
            file_handler = CustomTimedRotatingFileHandler(
                filename=str(LOG_DIR / "app.log"),
                when="midnight",
                backupCount=7,
                encoding="utf-8",
            )

            file_formatter = logging.Formatter(
                "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)

            console_handler = logging.StreamHandler()
            console_handler.setFormatter(file_formatter)
            logger.addHandler(console_handler)

        Logger._loggers[name] = logger
        return logger
