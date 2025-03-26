import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
import gzip
import shutil

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)


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
            file_handler = TimedRotatingFileHandler(
                filename=str(LOG_DIR / "app.log"),
                when="midnight",
                interval=1,
                backupCount=30,
                encoding="utf-8",
                utc=False,
            )

            file_handler.suffix = "%Y-%m-%d"
            file_handler.namer = lambda name: f"{name}.gz"
            file_handler.rotator = Logger._compress_log

            formatter = logging.Formatter(
                "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )

            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

        Logger._loggers[name] = logger
        return logger

    from typing import BinaryIO

    @staticmethod
    def _compress_log(source: str, dest: str):
        """Compress log files after rotation."""
        with open(source, "rb") as f_in, gzip.open(dest, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)
        Path(source).unlink()
