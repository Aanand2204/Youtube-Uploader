import logging
import os
from logging.handlers import RotatingFileHandler

# Logs are kept at project root / logs
_LOGS_DIR = os.path.join(os.getcwd(), "logs")
_LOG_FILE = os.path.join(_LOGS_DIR, "app.log")

_LOG_FORMAT = "[%(asctime)s] %(levelname)-8s | %(name)s | %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

_initialized = False

def _setup_root_logger() -> None:
    global _initialized
    if _initialized:
        return

    os.makedirs(_LOGS_DIR, exist_ok=True)

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT))

    file_handler = RotatingFileHandler(
        _LOG_FILE,
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT))

    root.addHandler(console_handler)
    root.addHandler(file_handler)
    _initialized = True

def get_logger(name: str) -> logging.Logger:
    _setup_root_logger()
    return logging.getLogger(name)
