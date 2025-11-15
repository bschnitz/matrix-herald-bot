from collections.abc import Mapping, MutableMapping
import logging
from logging import LoggerAdapter
from typing import Any

LOGGING_BASE_CONFIGURATION = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        },
        "json": {
            "format": '{"time": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "msg": "%(message)s"}'
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "level": "INFO",
        },
        "matrix_log_file": {
            "class": "logging.FileHandler",
            "formatter": "default",
            "filename": "logs/matrix.log",
            "level": "DEBUG",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    }
}

class BaseLogger(LoggerAdapter):
    lname: str = "root"
    config: dict = {}

    def __init__(self):
        logger = logging.getLogger(self.lname)
        super().__init__(logger, extra={})

    def process(
        self,
        msg: Any,
        kwargs: MutableMapping[str, Any]
    ) -> tuple[Any, MutableMapping[str, Any]]:
        raw_extra = kwargs.get("extra")
        user_extra: dict[str, Any] = dict(raw_extra) if isinstance(raw_extra, Mapping) else {}

        # self.extra kann None sein, absichern
        adapter_extra: dict[str, Any] = dict(self.extra) if isinstance(self.extra, Mapping) else {}

        merged = adapter_extra.copy()
        merged.update(user_extra)

        kwargs["extra"] = merged
        return msg, kwargs
