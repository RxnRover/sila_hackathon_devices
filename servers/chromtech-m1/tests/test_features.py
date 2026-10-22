import pytest

from unitelabs.chromtech_m1.features import KeypadController, MeteringPumpController
from unitelabs.chromtech_m1.io import ChromtechM1Protocol


@pytest.mark.parametrize(
    ("feature", "handlers"),
    [
        (
            MeteringPumpController,
            {"Start", "Stop", "IsRunning", "SetFlowRate", "FlowRate", "VolumeDispensed", "MaxFlowRate"},
        ),
        (KeypadController, {"Enable", "Disable", "IsEnabled"}),
    ],
)
def test_feature_exposes_abstract_base_feature(feature, handlers):
    # guards against overrides losing their SiLA decorator, which the CDK does not inherit from our ABFs
    instance = feature(ChromtechM1Protocol(port="", simulation=True))
    instance.attach()

    assert handlers <= set(instance._handlers)
