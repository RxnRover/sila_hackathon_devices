import dataclasses

MAX_FLOW_RATE = "10.00"


@dataclasses.dataclass
class SimulatedPump:
    """Stand-in for an M1-Class pump that answers SSI requests from memory."""

    flow_rate: float = 0.0
    is_running: bool = False
    is_keypad_enabled: bool = True

    def __call__(self, request: bytes) -> bytes:
        """Answers a request the way the pump would.

        :param request: Raw request, e.g. "FI123" followed by a carriage return
        :type request: bytes
        :return: Raw response, e.g. "OK/", or "Er/" for an invalid request
        :rtype: bytes
        """
        command = request.decode("ascii").strip().upper()
        code, value = command[:2], command[2:]
        decimals = len(MAX_FLOW_RATE.partition(".")[2])

        if code == "MF" and not value:
            return f"OK,MF:{MAX_FLOW_RATE}/".encode("ascii")
        if code == "FI" and value.isdigit():
            self.flow_rate = min(int(value) / 10**decimals, float(MAX_FLOW_RATE))
            return b"OK/"
        if code in ("RU", "ST") and not value:
            self.is_running = code == "RU"
            return b"OK/"
        if code in ("KE", "KD") and not value:
            self.is_keypad_enabled = code == "KE"
            return b"OK/"
        if code == "CS" and not value:
            return f"OK,{self.flow_rate:.{decimals}f},2500,0,PSI,0,{int(self.is_running)},0/".encode("ascii")
        if code == "PI" and not value:
            fields = [
                f"{self.flow_rate:.{decimals}f}",
                str(int(self.is_running)),
                "0",
                "10",
                "0",
                "1",
                "0",
                "0",
                "0",
                "0",
                "0",
                str(int(not self.is_keypad_enabled)),
                "0",
                "0",
                "0",
                "0",
                "0",
            ]
            return f"OK,{','.join(fields)}/".encode("ascii")

        return b"Er/"
