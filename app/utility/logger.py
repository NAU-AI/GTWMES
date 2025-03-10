import os
import logging
from logging.handlers import TimedRotatingFileHandler

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "..", "logs")
LOG_FILE = os.path.join(LOG_DIR, "equipment.log")

os.makedirs(LOG_DIR, exist_ok=True)


def delete_old_log_files(log_dir, max_files=7):
    log_files = [
        entry
        for entry in os.scandir(log_dir)
        if entry.is_file() and entry.name.startswith("equipment.log.")
    ]

    if len(log_files) > max_files:
        log_files.sort(key=lambda entry: entry.stat().st_ctime)

        files_to_delete = log_files[: len(log_files) - max_files]

        for file_entry in files_to_delete:
            os.remove(file_entry.path)


class Logger:
    @staticmethod
    def get_logger(name):
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)

        logger.handlers.clear()

        file_handler = TimedRotatingFileHandler(
            os.path.join(LOG_DIR, "equipment.log"),
            when="midnight",
            interval=1,
            backupCount=7,
            encoding="utf-8",
        )
        file_handler.suffix = "%Y-%m-%d"
        file_formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(file_formatter)
        logger.addHandler(console_handler)

        delete_old_log_files(LOG_DIR, max_files=7)

        return logger


logger = Logger.get_logger(__name__)
