from rxnrover.sila.abf import KeypadControllerBase
from unitelabs.cdk import sila

from ...io import ChromtechM1Protocol


class KeypadController(KeypadControllerBase):
    """Controls the front panel buttons of an M1-Class pump."""

    def __init__(self, protocol: ChromtechM1Protocol) -> None:
        """Instantiates the feature.

        :param protocol: Connection to the pump
        :type protocol: ChromtechM1Protocol
        """
        super().__init__(version="1.0", maturity_level="Draft")
        self._protocol = protocol

    # The CDK does not inherit decorators from ABFs outside of
    # `unitelabs.cdk.features`, so each override repeats its decorator.

    @sila.UnobservableCommand()
    async def enable(self) -> None:
        """Enables the keypad to allow physical operation."""
        await self._protocol.enable_keypad()

    @sila.UnobservableCommand()
    async def disable(self) -> None:
        """Disables the keypad to prevent physical operation."""
        await self._protocol.disable_keypad()

    @sila.UnobservableProperty()
    async def get_is_enabled(self) -> bool:
        """Gets the enabled state of the keypad.

        :return: Whether the keypad is enabled (True) or not (False)
        :rtype: bool
        """
        return await self._protocol.is_keypad_enabled()
