import os
import logging

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "..", "logs")
LOG_FILE = os.path.join(LOG_DIR, "equipment.log")

os.makedirs(LOG_DIR, exist_ok=True)


def truncate_log_if_exceeds(file_path, max_size=5 * 1024 * 1024):
    if os.path.exists(file_path) and os.path.getsize(file_path) > max_size:
        with open(file_path, "w") as f:
            f.truncate()


class Logger:
    @staticmethod
    def get_logger(name):
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)

        if not logger.hasHandlers():
            truncate_log_if_exceeds(LOG_FILE)  # Check size before logging

            file_handler = logging.FileHandler(LOG_FILE, mode="a")  # Append mode
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
