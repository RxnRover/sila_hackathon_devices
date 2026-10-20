import pytest
from rxnrover.sila.features.example_controller.example_controller import (
    ExampleController,
)


def test_create_concrete_feature():
    """A concrete feature should be able to be instantiated."""

    feature = ExampleController()

    assert feature.action() == 0
