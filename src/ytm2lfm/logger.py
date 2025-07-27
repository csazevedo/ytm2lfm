import logging
import logging.config
import sys
from typing import Any, Dict


class IncludeLevelFilter:
    def __init__(self, level: int) -> None:
        self.__level: int = level

    def filter(self, log_record: logging.LogRecord) -> bool:
        return log_record.levelno == self.__level


class ExcludeLevelFilter:
    def __init__(self, level: int) -> None:
        self.__level: int = level

    def filter(self, log_record: logging.LogRecord) -> bool:
        return log_record.levelno != self.__level  # Exclude this level


def setup_logging() -> None:
    """
    Configures the logging for the application. Should be called once at startup.
    """
    LOGGING_CONFIG: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {
            "info_only": {
                "()": IncludeLevelFilter,
                "level": logging.INFO,
            },
            "exclude_info": {
                "()": ExcludeLevelFilter,
                "level": logging.INFO,
            },
        },
        "formatters": {
            "standard": {"format": "%(asctime)s - %(name)-15s - %(levelname)-8s - %(message)s"},
        },
        "handlers": {
            "stdout": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "standard",
                "stream": sys.stdout,
                "filters": ["info_only"],
            },
            "stderr": {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
                "formatter": "standard",
                "stream": sys.stderr,
                "filters": ["exclude_info"],
            },
        },
        "loggers": {
            # Root logger: catches all logs from any module
            # "": {
            #     "level": "INFO",
            #     "handlers": ["stdout", "stderr"],
            # },
            # Specific logger for our module, can be more verbose
            "ytm2lfm": {
                "level": "DEBUG",
                "handlers": ["stdout", "stderr"],
                "propagate": False,
            },
        },
    }

    logging.config.dictConfig(LOGGING_CONFIG)
