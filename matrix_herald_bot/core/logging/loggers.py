import os
import sys
import inspect
import logging.config
from dotenv import load_dotenv
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

class MatrixTreeLogger(BaseLogger):
    lname = "herald.tree"
    config = {
        "handlers": ["tree_logger"],
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

    load_dotenv()
    logs_dir = os.getenv('LOGS_DIR') or './logs'
    logs_dir = os.path.abspath(os.path.expanduser(logs_dir))
    os.makedirs(logs_dir, exist_ok=True)

    for _, handler in config.get("handlers", {}).items():
        if "filename" in handler:
            handler["filename"] = os.path.join(logs_dir, os.path.basename(handler["filename"]))

    return config

logging.config.dictConfig(get_logging_config())


# bind all loggers to their class
class LoggerCollectionModule(Module):
    def configure(self, binder: Binder):
        for _, cls in inspect.getmembers(sys.modules[__name__], inspect.isclass):
            if issubclass(cls, BaseLogger) and cls is not BaseLogger:
                binder.bind(cls, to=cls, scope=singleton)
