"""Ponte entre o loop de tempo do Webots e o experimento neural abstrato.

Este módulo não importa ``controller``. Ele recebe valores de sensores e
devolve quatro velocidades, permitindo testes unitários fora do Webots.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
import math
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.control import MotorActionMapper  # noqa: E402
from src.experiments import (  # noqa: E402
    ExperimentConfig,
    ExperimentLogger,
    ExperimentRunner,
    MovementDirection,
)
from src.neural import (  # noqa: E402
    FourNeuronNetwork,
    NeuralConfig,
    SensoryInput,
    SensoryNormalization,
)


STOPPED_WHEELS = (0.0, 0.0, 0.0, 0.0)


@dataclass(frozen=True)
class GoalRegion:
    center_x: float
    center_y: float
    base_z: float
    width: float
    length: float
    height: float
    dwell_seconds: float

    @classmethod
    def from_controller_argument(cls, values) -> GoalRegion | None:
        if values is None:
            return None
        return cls(*values)

    def distance(self, position) -> float:
        """Menor distância horizontal do GPS ao retângulo da meta."""

        distance_x = max(abs(position[0] - self.center_x) - self.width / 2, 0.0)
        distance_y = max(abs(position[1] - self.center_y) - self.length / 2, 0.0)
        return math.hypot(distance_x, distance_y)

    def contains(self, position) -> bool:
        return (
            abs(position[0] - self.center_x) <= self.width / 2
            and abs(position[1] - self.center_y) <= self.length / 2
            and self.base_z <= position[2] <= self.base_z + self.height
        )


@dataclass(frozen=True)
class LearningRuntimeConfig:
    action_duration_seconds: float = 0.5
    wheel_speed: float = 3.0
    stationary_threshold: float = 0.005
    sound_intensity: float = 0.1
    acceleration_scale: float = 1.0
    random_seed: int = 42
    front_clockwise_sign: float = 1.0
    rear_clockwise_sign: float = 1.0

    def __post_init__(self) -> None:
        if self.action_duration_seconds <= 0:
            raise ValueError("action duration must be positive")
        if self.wheel_speed <= 0:
            raise ValueError("learning wheel speed must be positive")
        if self.stationary_threshold < 0:
            raise ValueError("stationary threshold cannot be negative")
        if self.sound_intensity < 0:
            raise ValueError("sound intensity cannot be negative")
        if self.acceleration_scale <= 0:
            raise ValueError("acceleration scale must be positive")
        if self.front_clockwise_sign not in (-1.0, 1.0):
            raise ValueError("front clockwise sign must be -1 or 1")
        if self.rear_clockwise_sign not in (-1.0, 1.0):
            raise ValueError("rear clockwise sign must be -1 or 1")


class LearningRuntime:
    """Executa uma ação neural por janela, preservando o controller multimodo."""

    def __init__(
        self,
        *,
        goal: GoalRegion | None,
        config: LearningRuntimeConfig | None = None,
        runs_directory: Path | None = None,
    ) -> None:
        self.goal = goal
        self.config = config or LearningRuntimeConfig()
        neural_config = NeuralConfig(
            random_seed=self.config.random_seed,
            sensory_normalization=SensoryNormalization(
                acceleration_scale=self.config.acceleration_scale,
            ),
        )
        experiment_config = ExperimentConfig(
            movement_duration_seconds=self.config.action_duration_seconds,
            stationary_threshold=self.config.stationary_threshold,
            sound_intensity=self.config.sound_intensity,
            # displacement = distância_final - distância_inicial;
            # aproximar-se da meta produz valor negativo.
            downhill_sign=-1,
            learning_streak=5,
        )
        self.network = FourNeuronNetwork(neural_config)
        self.runner = ExperimentRunner(self.network, experiment_config)
        self.mapper = MotorActionMapper(
            speed=self.config.wheel_speed,
            front_clockwise_sign=self.config.front_clockwise_sign,
            rear_clockwise_sign=self.config.rear_clockwise_sign,
        )
        self.runs_directory = runs_directory
        self.logger: ExperimentLogger | None = None
        self.active = False
        self.completed = False
        self.blocked_reason: str | None = None
        self._action_started_at = 0.0
        self._action_start_distance = 0.0
        self._acceleration_baseline = 0.0
        self._acceleration_samples: list[float] = []
        self._last_iteration = None

    def enter(self, *, time: float, position, longitudinal_acceleration: float) -> None:
        """Inicia ou retoma a janela da ação pendente."""

        if self.goal is None:
            self.active = False
            self.blocked_reason = "GOAL_NOT_CONFIGURED"
            return
        if self.completed:
            self.active = False
            return
        if self.runner.pending_action is None:
            self.runner.start(SensoryInput())
            self._open_logger()
        self.active = True
        self.blocked_reason = None
        self._acceleration_baseline = longitudinal_acceleration
        self._begin_action_window(time, position)

    def pause(self) -> None:
        self.active = False
        self._acceleration_samples.clear()

    def step(
        self,
        *,
        time: float,
        position,
        longitudinal_acceleration: float,
    ) -> tuple[float, float, float, float]:
        if not self.active or self.goal is None or self.completed:
            return STOPPED_WHEELS

        if self.goal.contains(position):
            self._acceleration_samples.append(
                abs(longitudinal_acceleration - self._acceleration_baseline)
            )
            # Registra também a ação parcial que efetivamente alcançou a meta.
            self._finish_action_window(time, position)
            self._complete("GOAL_REACHED")
            return STOPPED_WHEELS

        self._acceleration_samples.append(
            abs(longitudinal_acceleration - self._acceleration_baseline)
        )
        elapsed = time - self._action_started_at
        if elapsed + 1e-12 >= self.config.action_duration_seconds:
            self._finish_action_window(time, position)
            if not self.active or self.completed:
                return STOPPED_WHEELS

        action = self.runner.pending_action
        if action is None:
            return STOPPED_WHEELS
        return self.mapper.map(action).as_tuple()

    def telemetry(self) -> dict:
        action = self.runner.pending_action
        last = self._last_iteration
        if self.blocked_reason is not None:
            status = "BLOCKED"
        elif self.completed:
            status = "COMPLETED"
        elif self.active:
            status = "RUNNING"
        elif action is not None:
            status = "PAUSED"
        else:
            status = "READY"
        return {
            "status": status,
            "blockedReason": self.blocked_reason,
            "iteration": last.iteration if last is not None else 0,
            "winner": (
                last.neural_step.winner + 1
                if last is not None
                else (action.value + 1 if action is not None else None)
            ),
            "action": action.name if action is not None else None,
            "lastExecutedAction": (
                last.previous_action.name if last is not None else None
            ),
            "nextSelectedAction": action.name if action is not None else None,
            "direction": last.direction.value if last is not None else None,
            "maraca": (
                self.active and bool(last.rewarding_sound)
                if last is not None
                else False
            ),
            "lastRewardingSound": (
                bool(last.rewarding_sound) if last is not None else False
            ),
            "sameDirectionCount": (
                last.learning.same_direction_count if last is not None else 0
            ),
            "downwardCount": last.learning.downward_count if last is not None else 0,
            "paperCriterionReached": (
                last.learning.paper_criterion_reached if last is not None else False
            ),
            "downwardCriterionReached": (
                last.learning.downward_criterion_reached if last is not None else False
            ),
            "everPaperCriterionReached": (
                last.learning.ever_paper_criterion_reached
                if last is not None
                else False
            ),
            "everDownwardCriterionReached": (
                last.learning.ever_downward_criterion_reached
                if last is not None
                else False
            ),
            "firstPaperCriterionIteration": (
                last.learning.first_paper_criterion_iteration
                if last is not None
                else None
            ),
            "firstDownwardCriterionIteration": (
                last.learning.first_downward_criterion_iteration
                if last is not None
                else None
            ),
            "maximumSameDirectionCount": (
                last.learning.maximum_same_direction_count
                if last is not None
                else 0
            ),
            "maximumDownwardCount": (
                last.learning.maximum_downward_count if last is not None else 0
            ),
        }

    def _begin_action_window(self, time: float, position) -> None:
        self._action_started_at = time
        self._action_start_distance = self.goal.distance(position)
        self._acceleration_samples = []

    def _finish_action_window(self, time: float, position) -> None:
        final_distance = self.goal.distance(position)
        displacement = final_distance - self._action_start_distance
        acceleration = (
            sum(self._acceleration_samples) / len(self._acceleration_samples)
            if self._acceleration_samples
            else 0.0
        )
        result = self.runner.complete_iteration(
            displacement=displacement,
            acceleration=acceleration,
            visual=0.0,
        )
        self._last_iteration = result
        if self.logger is not None:
            self.logger.log_iteration(result)
        print(
            "Learning iteration "
            f"{result.iteration}: action={result.previous_action.name}, "
            f"direction={result.direction.value}, "
            f"maraca={result.rewarding_sound}, "
            f"next={result.next_action.name}"
        )

        self._begin_action_window(time, position)

    def _complete(self, reason: str) -> None:
        self.active = False
        self.completed = True
        self.blocked_reason = None
        if self.logger is not None:
            self.logger.write_summary(
                {
                    "completed": True,
                    "reason": reason,
                    "iterations": (
                        self._last_iteration.iteration + 1
                        if self._last_iteration is not None
                        else 0
                    ),
                    "learning": self.telemetry(),
                }
            )
        print(f"Learning experiment completed: {reason}")

    def _open_logger(self) -> None:
        if self.runs_directory is None or self.logger is not None:
            return
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        base_name = f"learning_{timestamp}_seed{self.config.random_seed}"
        run_directory = self.runs_directory / base_name
        suffix = 2
        while run_directory.exists():
            run_directory = self.runs_directory / f"{base_name}_{suffix}"
            suffix += 1
        self.logger = ExperimentLogger(
            run_directory,
            {
                "startedAtUtc": timestamp,
                "runtimeConfig": asdict(self.config),
                "neuralConfig": asdict(self.network.config),
                "experimentConfig": asdict(self.runner.config),
                "goal": asdict(self.goal) if self.goal is not None else None,
            },
        )
