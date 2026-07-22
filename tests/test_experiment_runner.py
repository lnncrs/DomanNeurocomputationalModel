import json

import pytest

from src.experiments import (
    ExperimentConfig,
    ExperimentLogger,
    ExperimentRunner,
    LearningCriterion,
    MovementDirection,
)
from src.neural import FourNeuronNetwork, NeuralConfig, SensoryInput


def test_runner_requires_explicit_start():
    runner = ExperimentRunner(FourNeuronNetwork())
    with pytest.raises(RuntimeError):
        runner.complete_iteration(displacement=-0.1, acceleration=0.2)


def test_downward_response_generates_sound_for_next_neural_step():
    runner = ExperimentRunner(
        FourNeuronNetwork(NeuralConfig(random_seed=1)),
        ExperimentConfig(sound_intensity=2.5, downhill_sign=-1),
    )
    first = runner.start(SensoryInput())
    assert first.sensory.sound == 0.0

    result = runner.complete_iteration(displacement=-0.02, acceleration=0.3)
    assert result.direction == MovementDirection.DOWN
    assert result.rewarding_sound is True
    assert result.sensory_input.sound == 2.5
    assert result.neural_step.sensory.sound == 2.5
    assert result.previous_action == first.action
    assert result.next_action == result.neural_step.action


@pytest.mark.parametrize(
    ("displacement", "expected"),
    [(-0.006, MovementDirection.DOWN), (0.006, MovementDirection.UP), (0.004, MovementDirection.STATIONARY)],
)
def test_direction_uses_threshold_and_configured_ramp_axis(displacement, expected):
    runner = ExperimentRunner(
        FourNeuronNetwork(),
        ExperimentConfig(stationary_threshold=0.005, downhill_sign=-1),
    )
    runner.start()
    assert runner.complete_iteration(
        displacement=displacement, acceleration=0.0
    ).direction == expected


def test_learning_criterion_distinguishes_paper_and_downward_goal():
    criterion = LearningCriterion(required_streak=5)
    up = None
    for _ in range(5):
        up = criterion.update(MovementDirection.UP)
    assert up is not None
    assert up.paper_criterion_reached is True
    assert up.downward_criterion_reached is False

    down = None
    for _ in range(5):
        down = criterion.update(MovementDirection.DOWN)
    assert down is not None
    assert down.paper_criterion_reached is True
    assert down.downward_criterion_reached is True
    assert down.ever_paper_criterion_reached is True
    assert down.ever_downward_criterion_reached is True
    assert down.first_paper_criterion_iteration == 4
    assert down.first_downward_criterion_iteration == 9
    assert down.maximum_same_direction_count == 5
    assert down.maximum_downward_count == 5


def test_learning_criterion_preserves_a_previously_reached_streak():
    criterion = LearningCriterion(required_streak=2)
    criterion.update(MovementDirection.DOWN)
    reached = criterion.update(MovementDirection.DOWN)
    interrupted = criterion.update(MovementDirection.STATIONARY)

    assert reached.downward_criterion_reached is True
    assert interrupted.downward_criterion_reached is False
    assert interrupted.ever_downward_criterion_reached is True
    assert interrupted.first_downward_criterion_iteration == 1
    assert interrupted.maximum_downward_count == 2


def test_logger_writes_metadata_iteration_and_summary(tmp_path):
    runner = ExperimentRunner(FourNeuronNetwork())
    runner.start()
    result = runner.complete_iteration(displacement=-0.02, acceleration=0.1)
    logger = ExperimentLogger(tmp_path / "run", {"seed": 0})
    logger.log_iteration(result)
    logger.write_summary({"success": True})
    report_path = logger.write_report()

    metadata = json.loads((tmp_path / "run" / "metadata.json").read_text())
    iteration = json.loads((tmp_path / "run" / "iterations.jsonl").read_text())
    summary = json.loads((tmp_path / "run" / "summary.json").read_text())
    assert metadata == {"seed": 0}
    assert iteration["direction"] == "DOWN"
    assert summary == {"success": True}
    report = report_path.read_text(encoding="utf-8")
    assert "Relatório do experimento neural" in report
    assert "Rede neural treinada" in report
    assert "Matriz final de pesos" in report
    assert "<svg" in report
