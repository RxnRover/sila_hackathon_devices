import collections.abc
from importlib.metadata import version

from unitelabs.cdk import Connector
from unitelabs.cdk.features.core.lock_controller import LockController

from .config import ChromtechM1Config
from .features import KeypadController, MeteringPumpController
from .io import ChromtechM1Protocol

__version__ = version("unitelabs-chromtech-m1")


async def create_app(config: ChromtechM1Config) -> collections.abc.AsyncGenerator[Connector, None]:
    """Create the connector application."""

    app = Connector(config)
    app.register(LockController())

    protocol = ChromtechM1Protocol(port=config.port, baudrate=config.baudrate, simulation=config.simulation_mode)

    try:
        await protocol.open()

        app.register(MeteringPumpController(protocol))
        app.register(KeypadController(protocol))

        yield app
    finally:
        protocol.close()
