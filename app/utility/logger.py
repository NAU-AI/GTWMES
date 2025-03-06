import os
import logging
from logging.handlers import RotatingFileHandler

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "..", "logs")
LOG_FILE = os.path.join(LOG_DIR, "equipment.log")

os.makedirs(LOG_DIR, exist_ok=True)


class Logger:
    @staticmethod
    def get_logger(name):
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)

        if not logger.hasHandlers():
            file_handler = RotatingFileHandler(
                LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3
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

        return logger


logger = Logger.get_logger(__name__)
