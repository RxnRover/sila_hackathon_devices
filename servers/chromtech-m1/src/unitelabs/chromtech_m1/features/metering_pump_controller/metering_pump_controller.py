from rxnrover.sila.abf import MeteringPumpControllerBase
from rxnrover.sila.abf.metering_pump_controller_base import InvalidFlowRate
from unitelabs.cdk import sila

from ...io import ChromtechM1Protocol


class MeteringPumpController(MeteringPumpControllerBase):
    """Controls an M1-Class metering pump. Flow rates are in mL/min."""

    def __init__(self, protocol: ChromtechM1Protocol) -> None:
        """Instantiates the feature.

        :param protocol: Connection to the pump
        :type protocol: ChromtechM1Protocol
        """
        super().__init__(version="1.0", maturity_level="Draft")
        self._protocol = protocol

    @sila.UnobservableCommand()
    async def start(self) -> None:
        """Starts the flow of the pump."""
        await self._protocol.run()

    @sila.UnobservableCommand()
    async def stop(self) -> None:
        """Stops the flow of the pump."""
        await self._protocol.stop()

    @sila.UnobservableProperty()
    async def is_running(self) -> bool:
        """Checks if the pump is currently running.

        :return: Whether the pump is running
        :rtype: bool
        """
        return (await self._protocol.get_status()).is_running

    @sila.UnobservableCommand(errors=[InvalidFlowRate])
    async def set_flow_rate(self, value: float) -> None:
        """Sets the flow rate for the pump.

        :raises InvalidFlowRate: Flow rate was outside of [0, max flow rate]

        :param value: Flow rate in mL/min
        :type value: float
        """
        if not 0 <= value <= self._protocol.max_flow_rate:
            msg = f"Flow rate must be between 0 and {self._protocol.max_flow_rate} mL/min, got {value}."
            raise InvalidFlowRate(msg)

        await self._protocol.set_flow_rate(value)

    @sila.UnobservableProperty()
    async def get_flow_rate(self) -> float:
        """Gets the current flow rate setting of the pump.

        :return: Flow rate in mL/min
        :rtype: float
        """
        return (await self._protocol.get_status()).flow_rate

    @sila.UnobservableProperty()
    async def get_volume_dispensed(self) -> float:
        """Gets the estimated volume dispensed since the last reset.

        The pump does not measure volume, so this is the flow rate integrated
        over the time the pump was running.

        :return: Volume dispensed in mL
        :rtype: float
        """
        return await self._protocol.get_volume_dispensed()

    @sila.UnobservableCommand()
    async def reset_volume_dispensed(self) -> None:
        """Resets the volume dispensed to zero."""
        self._protocol.reset_volume_dispensed()

    @sila.UnobservableProperty()
    async def get_max_flow_rate(self) -> float:
        """Gets the maximum allowable flow rate of the pump.

        :return: Maximum flow rate in mL/min
        :rtype: float
        """
        return self._protocol.max_flow_rate
