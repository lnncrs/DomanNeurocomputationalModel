from pathlib import Path
import sys

import pytest


CONTROLLER_DIRECTORY = (
    Path(__file__).resolve().parents[1]
    / "webots"
    / "controllers"
    / "four_wheels_manual"
)
if str(CONTROLLER_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(CONTROLLER_DIRECTORY))

from learning_runtime import (  # noqa: E402
    GoalRegion,
    LearningRuntime,
    LearningRuntimeConfig,
    STOPPED_WHEELS,
)


GOAL = GoalRegion(
    center_x=0.0,
    center_y=0.0,
    base_z=0.0,
    width=1.0,
    length=1.0,
    height=0.3,
    dwell_seconds=0.5,
)


def position(y: float, z: float = 0.1):
    return 0.0, y, z


def test_goal_distance_is_measured_to_rectangle_not_center():
    assert GOAL.distance(position(2.0)) == pytest.approx(1.5)
    assert GOAL.distance(position(0.5)) == pytest.approx(0.0)
    assert GOAL.distance(position(0.0)) == pytest.approx(0.0)


def test_goal_contains_checks_horizontal_area_and_height():
    assert GOAL.contains(position(0.0, 0.1)) is True
    assert GOAL.contains(position(0.6, 0.1)) is False
    assert GOAL.contains(position(0.0, 0.4)) is False


def test_missing_goal_blocks_learning_safely():
    runtime = LearningRuntime(goal=None)
    runtime.enter(time=0.0, position=position(2.0), longitudinal_acceleration=1.0)
    assert runtime.telemetry()["status"] == "BLOCKED"
    assert runtime.telemetry()["blockedReason"] == "GOAL_NOT_CONFIGURED"
    assert runtime.step(
        time=1.0,
        position=position(2.0),
        longitudinal_acceleration=1.0,
    ) == STOPPED_WHEELS


def test_action_is_held_until_window_finishes_and_uses_only_one_axle():
    runtime = LearningRuntime(
        goal=GOAL,
        config=LearningRuntimeConfig(
            action_duration_seconds=0.5,
            wheel_speed=3.0,
            random_seed=42,
        ),
    )
    runtime.enter(time=0.0, position=position(2.0), longitudinal_acceleration=2.0)
    first = runtime.step(
        time=0.0,
        position=position(2.0),
        longitudinal_acceleration=2.0,
    )
    held = runtime.step(
        time=0.25,
        position=position(1.99),
        longitudinal_acceleration=2.2,
    )
    assert held == first
    assert sum(value != 0.0 for value in first) == 2
    assert first[0] == first[1]
    assert first[2] == first[3]


def test_progress_during_action_generates_maraca_for_next_neural_step():
    runtime = LearningRuntime(
        goal=GOAL,
        config=LearningRuntimeConfig(action_duration_seconds=0.5, random_seed=1),
    )
    runtime.enter(time=0.0, position=position(2.0), longitudinal_acceleration=2.0)
    runtime.step(
        time=0.25,
        position=position(1.99),
        longitudinal_acceleration=2.4,
    )
    runtime.step(
        time=0.5,
        position=position(1.98),
        longitudinal_acceleration=2.2,
    )
    telemetry = runtime.telemetry()
    assert telemetry["iteration"] == 0
    assert telemetry["direction"] == "DOWN"
    assert telemetry["maraca"] is True
    assert runtime._last_iteration.sensory_input.sound == pytest.approx(0.1)
    assert runtime._last_iteration.sensory_input.acceleration == pytest.approx(0.3)


def test_five_downward_windows_mark_learning_but_continue_until_goal():
    runtime = LearningRuntime(
        goal=GOAL,
        config=LearningRuntimeConfig(action_duration_seconds=0.5, random_seed=3),
    )
    current_y = 2.0
    runtime.enter(
        time=0.0,
        position=position(current_y),
        longitudinal_acceleration=2.0,
    )
    for iteration in range(5):
        current_y -= 0.02
        command = runtime.step(
            time=(iteration + 1) * 0.5,
            position=position(current_y),
            longitudinal_acceleration=2.2,
        )
    assert runtime.completed is False
    assert runtime.telemetry()["status"] == "RUNNING"
    assert runtime.telemetry()["downwardCriterionReached"] is True
    assert runtime.telemetry()["everDownwardCriterionReached"] is True
    assert runtime.telemetry()["firstDownwardCriterionIteration"] == 4
    assert runtime.telemetry()["maximumDownwardCount"] == 5
    assert command != STOPPED_WHEELS

    command = runtime.step(
        time=3.0,
        position=position(0.0),
        longitudinal_acceleration=2.0,
    )
    assert runtime.completed is True
    assert runtime.telemetry()["status"] == "COMPLETED"
    assert runtime.telemetry()["maraca"] is False
    assert runtime.telemetry()["lastRewardingSound"] is True
    assert runtime.telemetry()["lastExecutedAction"] is not None
    assert runtime.telemetry()["nextSelectedAction"] is not None
    assert runtime.telemetry()["everDownwardCriterionReached"] is True
    assert runtime.telemetry()["firstDownwardCriterionIteration"] == 4
    assert command == STOPPED_WHEELS


def test_enter_creates_logs_only_when_directory_is_configured(tmp_path):
    runtime = LearningRuntime(
        goal=GOAL,
        config=LearningRuntimeConfig(action_duration_seconds=0.5, random_seed=9),
        runs_directory=tmp_path,
    )
    runtime.enter(time=0.0, position=position(2.0), longitudinal_acceleration=2.0)
    runtime.step(
        time=0.5,
        position=position(1.98),
        longitudinal_acceleration=2.1,
    )
    run_directories = list(tmp_path.iterdir())
    assert len(run_directories) == 1
    assert (run_directories[0] / "metadata.json").is_file()
    assert (run_directories[0] / "iterations.jsonl").is_file()
