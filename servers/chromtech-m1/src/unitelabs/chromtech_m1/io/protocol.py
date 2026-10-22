import asyncio
import dataclasses
import time

from unitelabs.bus import Protocol, create_serial_connection
from unitelabs.bus.testing import create_mock_connection

from .errors import PumpError
from .simulation import SimulatedPump
from .ssi import COMMAND_INTERVAL, SSICommand

OPEN_TIMEOUT = 5.0

PI_KEYPAD_FIELD = 11


@dataclasses.dataclass
class PumpStatus:
    """Run state and flow rate as reported by the pump."""

    flow_rate: float
    is_running: bool


class ChromtechM1Protocol(Protocol):
    """Serial connection to an M1-Class pump.

    The pump's USB port appears as a virtual COM port, so USB and RS-232 both
    connect through ``port``.
    """

    def __init__(self, port: str, baudrate: int = 9600, simulation: bool = False) -> None:
        """Instantiates the protocol.

        :param port: Serial port, e.g. "COM3" or "/dev/ttyUSB0"
        :type port: str
        :param baudrate: Baud rate set on the pump, 9600 or 19200
        :type baudrate: int
        :param simulation: Talk to a simulated pump instead of the serial port
        :type simulation: bool
        """
        if simulation:
            super().__init__(create_mock_connection, stubs=[SimulatedPump()], reconnect=False)
        else:
            super().__init__(create_serial_connection, port=port, baudrate=baudrate)

        self.max_flow_rate = 0.0
        self._flow_decimals = 0
        self._last_request = 0.0

        self._volume_dispensed = 0.0
        self._volume_status = PumpStatus(flow_rate=0.0, is_running=False)
        self._volume_since = time.monotonic()

    async def open(self) -> None:
        """Opens the port and reads the pump's flow range.

        :raises PumpError: The pump did not answer within ``OPEN_TIMEOUT``
        """
        try:
            await asyncio.wait_for(super().open(), timeout=OPEN_TIMEOUT)
        except (TimeoutError, asyncio.TimeoutError):
            self.close()
            msg = f"The pump did not answer within {OPEN_TIMEOUT} seconds."
            raise PumpError(msg) from None

    async def identity(self, **kwargs) -> bool:
        """Confirms a pump is attached by reading its maximum flow rate.

        :return: True once the pump has answered
        :rtype: bool
        """
        await self.read_max_flow_rate()
        return True

    async def run(self) -> None:
        """Starts the pump."""
        await self._send("RU")
        self._update_volume(is_running=True)

    async def stop(self) -> None:
        """Stops the pump."""
        await self._send("ST")
        self._update_volume(is_running=False)

    async def set_flow_rate(self, flow_rate: float) -> None:
        """Sets the flow rate.

        :param flow_rate: Flow rate in mL/min
        :type flow_rate: float
        """
        # "FI" takes an integer in units of the pump's resolution: with "MF:10.00", "FI123" is 1.23 mL/min
        await self._send(f"FI{round(flow_rate * 10**self._flow_decimals)}")
        self._update_volume(flow_rate=flow_rate)

    async def get_status(self) -> PumpStatus:
        """Gets the flow rate setting and run state.

        :return: Current status of the pump
        :rtype: PumpStatus
        """
        # OK,<flow>,<UPL>,<LPL>,<units>,0,<R/S>,0
        fields = await self._send("CS")
        status = PumpStatus(flow_rate=float(fields[0]), is_running=fields[5] == "1")
        self._update_volume(flow_rate=status.flow_rate, is_running=status.is_running)
        return status

    async def read_max_flow_rate(self) -> float:
        """Reads the maximum flow rate, which also sets the flow resolution.

        :return: Maximum flow rate in mL/min
        :rtype: float
        """
        # OK,MF:<max_flow>, where the number of decimals is the flow resolution
        value = (await self._send("MF"))[0].removeprefix("MF:")
        self.max_flow_rate = float(value)
        self._flow_decimals = len(value.partition(".")[2])
        return self.max_flow_rate

    async def get_volume_dispensed(self) -> float:
        """Gets the estimated volume dispensed since the last reset.

        The pump has no volume counter, so this integrates the flow rate over
        the time the pump was running. The status is re-read first to catch
        changes made on the front panel.

        :return: Volume dispensed in mL
        :rtype: float
        """
        await self.get_status()
        return self._volume_dispensed

    def reset_volume_dispensed(self) -> None:
        """Resets the volume dispensed to zero."""
        self._update_volume()
        self._volume_dispensed = 0.0

    async def enable_keypad(self) -> None:
        """Enables the front panel buttons."""
        await self._send("KE")

    async def disable_keypad(self) -> None:
        """Disables the front panel buttons."""
        await self._send("KD")

    async def is_keypad_enabled(self) -> bool:
        """Checks if the front panel buttons are enabled.

        :return: Whether the buttons are enabled
        :rtype: bool
        """
        fields = await self._send("PI")
        return fields[PI_KEYPAD_FIELD] == "0"

    async def _send(self, message: str) -> list[str]:
        """Sends a request, waiting the minimum interval SSI recommends.

        :param message: Request without terminator, e.g. "FI123"
        :type message: str
        :return: Response fields following "OK"
        :rtype: list[str]
        """
        delay = self._last_request + COMMAND_INTERVAL - time.monotonic()
        if delay > 0:
            await asyncio.sleep(delay)

        try:
            return await self.execute(SSICommand(message))
        finally:
            self._last_request = time.monotonic()

    def _update_volume(self, flow_rate: float | None = None, is_running: bool | None = None) -> None:
        """Adds the volume dispensed since the last update, then records the new state.

        :param flow_rate: New flow rate in mL/min, or None if unchanged
        :type flow_rate: float | None
        :param is_running: New run state, or None if unchanged
        :type is_running: bool | None
        """
        now = time.monotonic()
        if self._volume_status.is_running:
            self._volume_dispensed += self._volume_status.flow_rate * (now - self._volume_since) / 60

        self._volume_since = now
        if flow_rate is not None:
            self._volume_status.flow_rate = flow_rate
        if is_running is not None:
            self._volume_status.is_running = is_running
