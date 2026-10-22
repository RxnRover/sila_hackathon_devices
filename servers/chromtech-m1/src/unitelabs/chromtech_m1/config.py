import dataclasses
import typing
from importlib.metadata import version

from unitelabs.cdk import ConnectorBaseConfig, SiLAServerConfig

__version__ = version("unitelabs-chromtech-m1")


@dataclasses.dataclass
class ChromtechM1Config(ConnectorBaseConfig):
    """Configuration for the chromtech_m1."""

    port: str = "COM3"
    """Serial port of the pump, e.g. "COM3" or "/dev/ttyUSB0"; USB shows up as a virtual COM port."""

    baudrate: typing.Literal[9600, 19200] = 9600
    """Baud rate set in the pump's setup menu."""

    simulation_mode: bool = True
    """Whether to use a simulated pump instead of the hardware."""

    sila_server: SiLAServerConfig = dataclasses.field(
        default_factory=lambda: SiLAServerConfig(
            name="chromtech_m1",
            type="Pump",
            description=(
                """
                A connector for Chromtech M1 style pumps.
                """
            ),
            version=str(__version__),
            vendor_url="https://unitelabs.io/",
        )
    )
