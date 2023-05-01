import logging
import logging.config

from colorama import init  # type: ignore

from commitizen.cz.base import BaseCommitizen

init()


LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {"standard": {"format": "%(message)s"}},
    "handlers": {
        "default": {
            "level": "DEBUG",
            "formatter": "standard",
            "class": "logging.StreamHandler",
        }
    },
    "loggers": {
        "commitizen": {"handlers": ["default"], "level": "INFO", "propagate": True}
    },
}

logging.config.dictConfig(LOGGING)

__all__ = ["BaseCommitizen"]
