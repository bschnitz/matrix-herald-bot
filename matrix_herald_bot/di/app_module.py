from injector import Module, singleton, provider
from matrix_herald_bot.config.env_loader import build_configuration_from_env
from matrix_herald_bot.config.model import Configuration

class AppModule(Module):
    @singleton
    @provider
    def provide_configuration(self) -> Configuration:
        return build_configuration_from_env()
