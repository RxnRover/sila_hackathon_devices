import pytest

from unitelabs.chromtech_m1.io import ChromtechM1Protocol, PumpError
from unitelabs.chromtech_m1.io.ssi import parse_fields


@pytest.fixture
async def protocol():
    protocol = ChromtechM1Protocol(port="", simulation=True)
    await protocol.open()
    yield protocol
    protocol.close()


def test_parse_fields_drops_ok():
    assert parse_fields("OK,MF:10.00") == ["MF:10.00"]
    assert parse_fields("OK") == []


@pytest.mark.parametrize("response", ["Er", "garbage"])
def test_parse_fields_raises_on_error(response):
    with pytest.raises(PumpError):
        parse_fields(response)


async def test_open_reads_max_flow_rate(protocol):
    assert protocol.max_flow_rate == 10.0


async def test_set_flow_rate_scales_to_pump_resolution(protocol):
    await protocol.set_flow_rate(1.23)

    assert (await protocol.get_status()).flow_rate == 1.23


async def test_run_and_stop(protocol):
    await protocol.run()
    assert (await protocol.get_status()).is_running

    await protocol.stop()
    assert not (await protocol.get_status()).is_running


async def test_volume_dispensed_only_accumulates_while_running(protocol):
    await protocol.set_flow_rate(6.0)
    assert await protocol.get_volume_dispensed() == 0

    await protocol.run()
    await protocol.stop()
    volume = await protocol.get_volume_dispensed()
    assert volume > 0
    assert await protocol.get_volume_dispensed() == volume

    protocol.reset_volume_dispensed()
    assert await protocol.get_volume_dispensed() == 0


async def test_keypad(protocol):
    await protocol.disable_keypad()
    assert not await protocol.is_keypad_enabled()

    await protocol.enable_keypad()
    assert await protocol.is_keypad_enabled()
