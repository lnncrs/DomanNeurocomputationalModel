"""Protocolo temporal do experimento, independente do Webots"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import math

from src.neural import FourNeuronNetwork, MotorAction, NeuralStepResult, SensoryInput

from .sensory_processing import SensoryObservation, SensoryProcessor


class MovementDirection(str, Enum):
    DOWN = "DOWN"
    UP = "UP"
    STATIONARY = "STATIONARY"


@dataclass(frozen=True)
class ExperimentConfig:
    # A duração é consumida pelo runtime ou por outro driver, não por esta classe.
    movement_duration_seconds: float = 0.5
    stationary_threshold: float = 0.005
    sound_intensity: float = 0.1
    downhill_sign: int = -1
    learning_streak: int = 5

    def __post_init__(self) -> None:
        if self.movement_duration_seconds <= 0:
            raise ValueError("movement_duration_seconds must be positive")
        if self.stationary_threshold < 0:
            raise ValueError("stationary_threshold cannot be negative")
        if self.sound_intensity < 0:
            raise ValueError("sound_intensity cannot be negative")
        if self.downhill_sign not in (-1, 1):
            raise ValueError("downhill_sign must be -1 or 1")
        if self.learning_streak <= 0:
            raise ValueError("learning_streak must be positive")


@dataclass(frozen=True)
class LearningStatus:
    same_direction_count: int
    downward_count: int
    paper_criterion_reached: bool
    downward_criterion_reached: bool
    ever_paper_criterion_reached: bool
    ever_downward_criterion_reached: bool
    first_paper_criterion_iteration: int | None
    first_downward_criterion_iteration: int | None
    maximum_same_direction_count: int
    maximum_downward_count: int


class LearningCriterion:
    """Mantém separados o critério literal e o objetivo de descida."""

    def __init__(self, required_streak: int = 5) -> None:
        self.required_streak = required_streak
        self.reset()

    def reset(self) -> None:
        self._last_direction: MovementDirection | None = None
        self._same_direction_count = 0
        self._downward_count = 0
        self._iteration = 0
        self._first_paper_criterion_iteration: int | None = None
        self._first_downward_criterion_iteration: int | None = None
        self._maximum_same_direction_count = 0
        self._maximum_downward_count = 0

    def update(self, direction: MovementDirection) -> LearningStatus:
        self._update_streaks(direction)

        paper_criterion_reached = (
            direction != MovementDirection.STATIONARY
            and self._same_direction_count >= self.required_streak
        )
        downward_criterion_reached = self._downward_count >= self.required_streak

        if (
            paper_criterion_reached
            and self._first_paper_criterion_iteration is None
        ):
            self._first_paper_criterion_iteration = self._iteration
        if (
            downward_criterion_reached
            and self._first_downward_criterion_iteration is None
        ):
            self._first_downward_criterion_iteration = self._iteration

        self._maximum_same_direction_count = max(
            self._maximum_same_direction_count, self._same_direction_count
        )
        self._maximum_downward_count = max(
            self._maximum_downward_count, self._downward_count
        )

        status = LearningStatus(
            same_direction_count=self._same_direction_count,
            downward_count=self._downward_count,
            paper_criterion_reached=paper_criterion_reached,
            downward_criterion_reached=downward_criterion_reached,
            ever_paper_criterion_reached=(
                self._first_paper_criterion_iteration is not None
            ),
            ever_downward_criterion_reached=(
                self._first_downward_criterion_iteration is not None
            ),
            first_paper_criterion_iteration=self._first_paper_criterion_iteration,
            first_downward_criterion_iteration=(
                self._first_downward_criterion_iteration
            ),
            maximum_same_direction_count=self._maximum_same_direction_count,
            maximum_downward_count=self._maximum_downward_count,
        )
        self._iteration += 1
        return status

    def _update_streaks(self, direction: MovementDirection) -> None:
        """Atualiza as sequências atual e descendente."""

        if direction == self._last_direction:
            self._same_direction_count += 1
        else:
            self._last_direction = direction
            self._same_direction_count = 1

        if direction == MovementDirection.DOWN:
            self._downward_count += 1
        else:
            self._downward_count = 0


@dataclass(frozen=True)
class ExperimentIterationResult:
    iteration: int
    previous_action: MotorAction
    displacement: float
    direction: MovementDirection
    rewarding_sound: bool
    sensory_observation: SensoryObservation
    sensory_input: SensoryInput
    neural_step: NeuralStepResult
    learning: LearningStatus
    next_action: MotorAction


class ExperimentRunner:
    """Preserva a causalidade ação -> ambiente -> sensores -> próxima ação."""

    def __init__(
        self,
        network: FourNeuronNetwork,
        config: ExperimentConfig | None = None,
        sensory_processor: SensoryProcessor | None = None,
    ) -> None:
        self.network = network
        self.config = config or ExperimentConfig()
        self.sensory_processor = sensory_processor or SensoryProcessor()
        self.criterion = LearningCriterion(self.config.learning_streak)
        self._pending_action: MotorAction | None = None
        self._iteration = 0

    @property
    def pending_action(self) -> MotorAction | None:
        return self._pending_action

    def start(self, initial_sensory: SensoryInput | None = None) -> NeuralStepResult:
        """
        Seleciona a primeira ação antes de existir resposta física.

        Quando fornecida, ``initial_sensory`` já deve estar normalizada. Em uma
        execução comum, a ausência de observação anterior produz três
        intensidades iguais a zero.
        """

        if self._pending_action is not None:
            raise RuntimeError("experiment has already started")
        neural_step = self.network.step(initial_sensory or SensoryInput())
        self._pending_action = neural_step.action
        return neural_step

    def complete_iteration(
        self,
        *,
        displacement: float,
        acceleration: float,
        visual: float = 0.0,
    ) -> ExperimentIterationResult:
        """Registra a consequência da ação anterior e escolhe a seguinte.

        ``displacement`` usa o eixo escolhido pelo experimento. O sinal definido
        por ``downhill_sign`` representa descida. A maraca é criada somente
        depois dessa classificação e entra no passo neural subsequente.
        """

        if self._pending_action is None:
            raise RuntimeError("call start() before completing an iteration")
        if (
            not math.isfinite(displacement)
            or not math.isfinite(acceleration)
            or not math.isfinite(visual)
        ):
            raise ValueError("iteration observations must be finite")

        previous_action = self._pending_action

        # A resposta do ambiente determina direção e estímulos sensoriais.
        direction = self._classify_movement(displacement)
        rewarding_sound = direction == MovementDirection.DOWN
        sensory_observation = SensoryObservation(
            acceleration=acceleration,
            visual=visual,
            sound=self.config.sound_intensity if rewarding_sound else 0.0,
        )
        sensory_input = self.sensory_processor.process(sensory_observation)

        # As intensidades já processadas resultantes da ação anterior
        # selecionam a próxima ação.
        neural_step = self.network.step(sensory_input)
        next_action = neural_step.action
        learning = self.criterion.update(direction)

        result = ExperimentIterationResult(
            iteration=self._iteration,
            previous_action=previous_action,
            displacement=displacement,
            direction=direction,
            rewarding_sound=rewarding_sound,
            sensory_observation=sensory_observation,
            sensory_input=sensory_input,
            neural_step=neural_step,
            learning=learning,
            next_action=next_action,
        )
        self._pending_action = next_action
        self._iteration += 1
        return result

    def _classify_movement(self, displacement: float) -> MovementDirection:
        directed = displacement * self.config.downhill_sign
        if directed > self.config.stationary_threshold:
            return MovementDirection.DOWN
        if directed < -self.config.stationary_threshold:
            return MovementDirection.UP
        return MovementDirection.STATIONARY
