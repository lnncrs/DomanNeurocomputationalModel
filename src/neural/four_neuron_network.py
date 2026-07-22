"""Rede recorrente de quatro neurônios descrita por Ropero Peláez e Santana.

O módulo não depende do Webots. As equações publicadas são mantidas próximas
da ordem temporal em que são executadas, facilitando auditoria científica.
Hipóteses necessárias para completar a descrição do artigo são configuráveis
e documentadas em ``src/neural/README.md``.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import math
import random
from typing import Sequence


NEURON_COUNT = 4


class MotorAction(Enum):
    """Primitivas motoras abstratas associadas aos quatro neurônios."""

    FRONT_CLOCKWISE = 0
    FRONT_COUNTERCLOCKWISE = 1
    REAR_CLOCKWISE = 2
    REAR_COUNTERCLOCKWISE = 3


class CompetitionMode(str, Enum):
    DETERMINISTIC = "deterministic"
    STOCHASTIC = "stochastic"


class PlasticityScope(str, Enum):
    WINNER_ONLY = "winner_only"
    ALL_POSTSYNAPTIC = "all_postsynaptic"


class IntrinsicOutputSource(str, Enum):
    POST_COMPETITION = "post_competition"
    PRE_COMPETITION = "pre_competition"


@dataclass(frozen=True)
class SensoryInput:
    """Valores sensoriais brutos de uma iteração experimental."""

    acceleration: float = 0.0
    visual: float = 0.0
    sound: float = 0.0


@dataclass(frozen=True)
class SensoryNormalization:
    """Transformação linear explícita aplicada a cada canal sensorial."""

    acceleration_offset: float = 0.0
    acceleration_scale: float = 1.0
    visual_offset: float = 0.0
    visual_scale: float = 1.0
    sound_offset: float = 0.0
    sound_scale: float = 1.0

    def normalize(self, sensory: SensoryInput) -> NormalizedSensoryInput:
        acceleration = (
            sensory.acceleration - self.acceleration_offset
        ) * self.acceleration_scale
        visual = (sensory.visual - self.visual_offset) * self.visual_scale
        sound = (sensory.sound - self.sound_offset) * self.sound_scale
        values = (acceleration, visual, sound)
        if not all(math.isfinite(value) for value in values):
            raise ValueError("normalized sensory values must be finite")
        return NormalizedSensoryInput(
            acceleration=acceleration,
            visual=visual,
            sound=sound,
            total=sum(values),
        )


@dataclass(frozen=True)
class NormalizedSensoryInput:
    acceleration: float
    visual: float
    sound: float
    total: float


@dataclass(frozen=True)
class NeuralConfig:
    """Parâmetros publicados e hipóteses operacionais da reconstrução."""

    neuron_count: int = NEURON_COUNT
    recurrent_weight: float = 0.7
    sigmoid_gain: float = 25.0
    synaptic_learning_rate: float = 0.01
    intrinsic_learning_rate: float = 0.01
    initial_shift: float = 0.5
    initial_weight_min: float = 0.1
    initial_weight_max: float = 0.9
    competition_mode: CompetitionMode = CompetitionMode.DETERMINISTIC
    plasticity_scope: PlasticityScope = PlasticityScope.WINNER_ONLY
    intrinsic_output_source: IntrinsicOutputSource = (
        IntrinsicOutputSource.POST_COMPETITION
    )
    activation_noise_std: float = 0.0
    random_seed: int = 0
    optional_weight_bounds: tuple[float, float] | None = None
    sensory_normalization: SensoryNormalization = SensoryNormalization()

    def __post_init__(self) -> None:
        if self.neuron_count != NEURON_COUNT:
            raise ValueError("the article architecture requires exactly 4 neurons")
        if self.sigmoid_gain <= 0:
            raise ValueError("sigmoid_gain must be positive")
        if self.synaptic_learning_rate < 0 or self.intrinsic_learning_rate < 0:
            raise ValueError("learning rates cannot be negative")
        if self.initial_weight_min > self.initial_weight_max:
            raise ValueError("initial weight range is inverted")
        if self.activation_noise_std < 0:
            raise ValueError("activation_noise_std cannot be negative")
        if self.optional_weight_bounds is not None:
            lower, upper = self.optional_weight_bounds
            if lower > upper:
                raise ValueError("weight bounds are inverted")


Matrix = tuple[tuple[float, ...], ...]


@dataclass(frozen=True)
class NeuralStepResult:
    step_index: int
    sensory: NormalizedSensoryInput
    activation: tuple[float, ...]
    raw_output: tuple[float, ...]
    competitive_output: tuple[float, ...]
    previous_competitive_output: tuple[float, ...]
    shifts_before: tuple[float, ...]
    shifts_after: tuple[float, ...]
    weights_before: Matrix
    weights_after: Matrix
    winner: int
    action: MotorAction


def _matrix_copy(matrix: Sequence[Sequence[float]]) -> Matrix:
    return tuple(tuple(row) for row in matrix)


def _stable_sigmoid(value: float) -> float:
    if value >= 0:
        return 1.0 / (1.0 + math.exp(-value))
    exponential = math.exp(value)
    return exponential / (1.0 + exponential)


def sigmoid_output(activation: float, shift: float, gain: float = 25.0) -> float:
    """Equação 3 do artigo, com proteção numérica contra overflow."""

    return _stable_sigmoid(gain * (activation - shift))


def grossberg_delta(
    *, input_j: float, activation_i: float, weight_ij: float, epsilon: float
) -> float:
    """Equação 2: variação do peso da conexão j -> i."""

    return epsilon * input_j * (activation_i - weight_ij)


def intrinsic_shift(*, previous_shift: float, output: float, xi: float) -> float:
    """Equação 4, escrita como atualização do instante t para t + 1."""

    return (xi * output + previous_shift) / (1.0 + xi)


class FourNeuronNetwork:
    """Rede excitadora rate-code, recorrente, plástica e competitiva."""

    def __init__(self, config: NeuralConfig | None = None) -> None:
        self.config = config or NeuralConfig()
        self._rng = random.Random(self.config.random_seed)
        self.reset()

    @property
    def weights(self) -> Matrix:
        return _matrix_copy(self._weights)

    @property
    def shifts(self) -> tuple[float, ...]:
        return tuple(self._shifts)

    @property
    def previous_competitive_output(self) -> tuple[float, ...]:
        return tuple(self._previous_competitive_output)

    def reset(self) -> None:
        """Restaura estado e RNG; a mesma seed reproduz a mesma rede."""

        self._rng.seed(self.config.random_seed)
        self._weights = [
            [
                self.config.recurrent_weight
                if i == j
                else self._rng.uniform(
                    self.config.initial_weight_min,
                    self.config.initial_weight_max,
                )
                for j in range(NEURON_COUNT)
            ]
            for i in range(NEURON_COUNT)
        ]
        self._shifts = [self.config.initial_shift] * NEURON_COUNT
        self._previous_competitive_output = [0.0] * NEURON_COUNT
        self._step_index = 0

    def step(self, sensory_input: SensoryInput) -> NeuralStepResult:
        """Processa o feedback da ação anterior e escolhe a próxima ação."""

        sensory = self.config.sensory_normalization.normalize(sensory_input)
        weights_before = self.weights
        shifts_before = self.shifts
        previous_output = self.previous_competitive_output

        activation = tuple(
            sensory.total
            + sum(
                self._weights[i][j] * self._previous_competitive_output[j]
                for j in range(NEURON_COUNT)
            )
            + (
                self._rng.gauss(0.0, self.config.activation_noise_std)
                if self.config.activation_noise_std > 0
                else 0.0
            )
            for i in range(NEURON_COUNT)
        )
        raw_output = tuple(
            sigmoid_output(
                activation[i], self._shifts[i], self.config.sigmoid_gain
            )
            for i in range(NEURON_COUNT)
        )
        winner = self._select_winner(raw_output)
        competitive_output = tuple(
            raw_output[i] if i == winner else 0.0 for i in range(NEURON_COUNT)
        )

        self._update_synaptic_weights(
            activation=activation,
            previous_output=previous_output,
            current_winner=winner,
        )
        self._update_intrinsic_shifts(raw_output, competitive_output)
        self._previous_competitive_output = list(competitive_output)

        result = NeuralStepResult(
            step_index=self._step_index,
            sensory=sensory,
            activation=activation,
            raw_output=raw_output,
            competitive_output=competitive_output,
            previous_competitive_output=previous_output,
            shifts_before=shifts_before,
            shifts_after=self.shifts,
            weights_before=weights_before,
            weights_after=self.weights,
            winner=winner,
            action=MotorAction(winner),
        )
        self._step_index += 1
        return result

    def _select_winner(self, raw_output: tuple[float, ...]) -> int:
        if self.config.competition_mode == CompetitionMode.STOCHASTIC:
            total = sum(raw_output)
            if total <= 0:
                return self._rng.randrange(NEURON_COUNT)
            threshold = self._rng.random() * total
            accumulated = 0.0
            for index, output in enumerate(raw_output):
                accumulated += output
                if accumulated >= threshold:
                    return index
            return NEURON_COUNT - 1

        maximum = max(raw_output)
        tied = [
            index
            for index, output in enumerate(raw_output)
            if math.isclose(output, maximum, rel_tol=0.0, abs_tol=1e-15)
        ]
        return self._rng.choice(tied)

    def _update_synaptic_weights(
        self,
        activation: tuple[float, ...],
        previous_output: tuple[float, ...],
        current_winner: int,
    ) -> None:
        if self.config.plasticity_scope == PlasticityScope.WINNER_ONLY:
            postsynaptic_indices = (current_winner,)
        else:
            postsynaptic_indices = range(NEURON_COUNT)

        epsilon = self.config.synaptic_learning_rate
        for i in postsynaptic_indices:
            for j in range(NEURON_COUNT):
                if i == j:
                    continue
                old_weight = self._weights[i][j]
                delta = grossberg_delta(
                    input_j=previous_output[j],
                    activation_i=activation[i],
                    weight_ij=old_weight,
                    epsilon=epsilon,
                )
                new_weight = old_weight + delta
                if self.config.optional_weight_bounds is not None:
                    lower, upper = self.config.optional_weight_bounds
                    new_weight = min(upper, max(lower, new_weight))
                self._weights[i][j] = new_weight

        # Reafirma a invariável publicada, inclusive contra futuras alterações.
        for i in range(NEURON_COUNT):
            self._weights[i][i] = self.config.recurrent_weight

    def _update_intrinsic_shifts(
        self,
        raw_output: tuple[float, ...],
        competitive_output: tuple[float, ...],
    ) -> None:
        if (
            self.config.intrinsic_output_source
            == IntrinsicOutputSource.POST_COMPETITION
        ):
            source = competitive_output
        else:
            source = raw_output

        xi = self.config.intrinsic_learning_rate
        self._shifts = [
            intrinsic_shift(previous_shift=self._shifts[i], output=source[i], xi=xi)
            for i in range(NEURON_COUNT)
        ]
