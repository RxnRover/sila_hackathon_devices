"""Teledyne SSI serial pump protocol used by the M1-Class pump.

Requests are a two-letter code plus optional digits, ended by a
carriage return. Responses are "OK" with comma-separated fields, or "Er" for an
invalid command, and always end with "/".
"""

from unitelabs.bus import SerialCommand

from .errors import PumpError

RESPONSE_TIMEOUT = 1.0

COMMAND_INTERVAL = 0.1


def parse_fields(response: str) -> list[str]:
    """Splits a response into the fields that follow "OK".

    :raises PumpError: The pump answered "Er" or something other than "OK"

    :param response: Response without the "/" terminator, e.g. "OK,MF:10.00"
    :type response: str
    :return: Fields after "OK", e.g. ["MF:10.00"]
    :rtype: list[str]
    """
    response = response.strip()
    if response.upper().startswith("ER"):
        msg = "The pump rejected the command."
        raise PumpError(msg)
    if not response.upper().startswith("OK"):
        msg = f"Unexpected response from the pump: {response!r}."
        raise PumpError(msg)

    return [field.strip() for field in response.split(",")[1:]]


class SSICommand(SerialCommand):
    """Request to an SSI pump that resolves to the fields following "OK"."""

    def __new__(cls, *args, **kwargs):
        """Creates the command with the response parser attached."""
        return super().__new__(cls, *args, **kwargs).add_parser(parse_fields)

    def __init__(self, message: str) -> None:
        """Instantiates the command.

        :param message: Request without terminator, e.g. "FI123"
        :type message: str
        """
        super().__init__(message, read_terminator=b"/", write_terminator=b"\r", timeout=RESPONSE_TIMEOUT)
