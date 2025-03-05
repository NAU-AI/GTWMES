import os
import logging
from logging.handlers import RotatingFileHandler

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "equipment.log")
os.makedirs(LOG_DIR, exist_ok=True)


class Logger:
    @staticmethod
    def get_logger(name):
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            log_handler = RotatingFileHandler(
                LOG_FILE,
                maxBytes=5 * 1024 * 1024,
                backupCount=3,  # 5MB per file, keep 3 backups
            )
            log_formatter = logging.Formatter(
                "%(asctime)s - %(levelname)s - %(message)s"
            )
            log_handler.setFormatter(log_formatter)

            logger.addHandler(log_handler)
            logger.addHandler(logging.StreamHandler())
        return logger


logger = Logger.get_logger(__name__)
