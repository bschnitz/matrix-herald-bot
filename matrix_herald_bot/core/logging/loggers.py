import sys
import inspect
import logging.config
import yaml
from injector import Module, Binder, singleton
from matrix_herald_bot.root import config_dir

from matrix_herald_bot.core.logging.base import BaseLogger

class MatrixLogger(BaseLogger):
    lname = "herald.matrix"
    config = {
        "handlers": ["console", "matrix_log_file"],
        "level": "DEBUG",
        "propagate": False
    }

class CoreLogger(BaseLogger):
    lname = "herald.core"
    config = {
        "handlers": ["console", "core_log_file"],
        "level": "DEBUG",
        "propagate": False
    }


def get_logging_config():
    current_module = sys.modules[__name__]

    with open(f"{config_dir}/logging.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    if "loggers" not in config:
        config["loggers"] = {}

    for _, cls in inspect.getmembers(current_module, inspect.isclass):
        if issubclass(cls, BaseLogger) and cls is not BaseLogger:
            if cls.lname in config["loggers"] and cls.config:
                raise ValueError(f"Logger {cls.lname} already defined in LOGGING")

            config["loggers"][cls.lname] = cls.config

    return config

logging.config.dictConfig(get_logging_config())


# bind all loggers to their class
class LoggerCollectionModule(Module):
    def configure(self, binder: Binder):
        for _, cls in inspect.getmembers(sys.modules[__name__], inspect.isclass):
            if issubclass(cls, BaseLogger) and cls is not BaseLogger:
                binder.bind(cls, to=cls, scope=singleton)
