import math

import pytest

from src.experiments import (
    SensoryNormalization,
    SensoryObservation,
    SensoryProcessor,
)
from src.neural import SensoryInput


def test_processing_is_explicit_and_returns_summed_neural_input():
    processor = SensoryProcessor(
        SensoryNormalization(
            acceleration_offset=1.0,
            acceleration_scale=0.5,
            visual_scale=2.0,
            sound_scale=3.0,
        )
    )

    result = processor.process(SensoryObservation(3.0, 0.25, 0.5))

    assert isinstance(result, SensoryInput)
    assert result.acceleration == pytest.approx(1.0)
    assert result.visual == pytest.approx(0.5)
    assert result.sound == pytest.approx(1.5)
    assert result.total == pytest.approx(3.0)


def test_observation_rejects_non_finite_physical_values():
    with pytest.raises(ValueError, match="finite"):
        SensoryObservation(sound=math.nan)


def test_normalization_rejects_non_finite_parameters():
    with pytest.raises(ValueError, match="finite"):
        SensoryNormalization(visual_scale=math.inf)
