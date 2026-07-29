"""Rede recorrente de quatro neurônios descrita por Ropero Peláez e Santana."""

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


class PlasticityScope(str, Enum):
    """
    Hipóteses alternativas para o escopo da atualização sináptica.

    A publicação apresenta a regra de Grossberg, mas não descreve de maneira
    suficiente sua aplicação computacional após a competição entre os quatro
    neurônios.
    """

    WINNER_ONLY = "winner_only"
    ALL_POSTSYNAPTIC = "all_postsynaptic"


@dataclass(frozen=True)
class SensoryInput:
    """Intensidades sensoriais já normalizadas para uma iteração."""

    acceleration: float = 0.0
    visual: float = 0.0
    sound: float = 0.0

    def __post_init__(self) -> None:
        if not all(
            math.isfinite(value)
            for value in (self.acceleration, self.visual, self.sound)
        ):
            raise ValueError("sensory intensities must be finite")

    @property
    def total(self) -> float:
        """Soma sensorial comum apresentada aos quatro neurônios."""

        return self.acceleration + self.visual + self.sound


@dataclass(frozen=True)
class NeuralConfig:
    """Parâmetros da rede e hipóteses adotadas na reconstrução."""

    # Valores explicitamente apresentados no artigo.
    recurrent_weight: float = 0.7
    sigmoid_gain: float = 25.0

    # O artigo informa que xi varia entre 0.1 e 0.0001, mas não fixa um único
    # valor para todos os experimentos.
    intrinsic_learning_rate: float = 0.01

    # Hipóteses operacionais: valores não especificados claramente na
    # publicação e que devem ser avaliados experimentalmente.
    synaptic_learning_rate: float = 0.01
    initial_shift: float = 0.5
    initial_weight_min: float = 0.1
    initial_weight_max: float = 0.9
    plasticity_scope: PlasticityScope = PlasticityScope.WINNER_ONLY
    random_seed: int = 0

    def __post_init__(self) -> None:
        if self.sigmoid_gain <= 0:
            raise ValueError("sigmoid_gain must be positive")
        if self.synaptic_learning_rate < 0 or self.intrinsic_learning_rate < 0:
            raise ValueError("learning rates cannot be negative")
        if self.initial_weight_min > self.initial_weight_max:
            raise ValueError("initial weight range is inverted")


Matrix = tuple[tuple[float, ...], ...]


@dataclass(frozen=True)
class NeuralStepResult:
    """Registro imutável do estado e do resultado de uma iteração neural."""

    step_index: int
    sensory: SensoryInput
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


def sigmoid_output(
    activation: float,
    shift: float,
    gain: float = 25.0,
) -> float:
    """
    Calcula a saída rate-code pela função sigmoidal da Equação 3.

    ``gain`` controla a inclinação da curva; o artigo utiliza 25, mas não
    apresenta uma análise específica justificando esse valor. ``shift``
    representa o limiar adaptável associado à plasticidade intrínseca.
    """

    return _stable_sigmoid(gain * (activation - shift))


def grossberg_delta(
    *,
    input_j: float,
    activation_i: float,
    weight_ij: float,
    epsilon: float,
) -> float:
    """
    Calcula a variação do peso da conexão j -> i pela Equação 2.

    A atualização depende da atividade pré-sináptica de j, da ativação
    pós-sináptica de i e do peso atual. O termo
    ``(activation_i - weight_ij)`` limita o crescimento irrestrito e permite
    aumento ou redução do peso.
    """

    return epsilon * input_j * (activation_i - weight_ij)


def intrinsic_shift(*, previous_shift: float, output: float, xi: float) -> float:
    """
    Atualiza o shift da função sigmoidal pela Equação 4.

    Atividade elevada tende a deslocar a sigmoide para a direita, reduzindo a
    excitabilidade futura. Atividade baixa tende a deslocá-la para a esquerda,
    aumentando a excitabilidade.
    """

    return (xi * output + previous_shift) / (1.0 + xi)


def _stable_sigmoid(value: float) -> float:
    """Avalia a sigmoide sem provocar overflow numérico."""

    if value >= 0:
        return 1.0 / (1.0 + math.exp(-value))
    exponential = math.exp(value)
    return exponential / (1.0 + exponential)


def _matrix_copy(matrix: Sequence[Sequence[float]]) -> Matrix:
    return tuple(tuple(row) for row in matrix)


class FourNeuronNetwork:
    """
    Rede recorrente, excitatória e competitiva de quatro neurônios.

    Convenção da matriz:
        ``weights[target][source]`` representa a conexão dirigida do neurônio
        ``source`` para o neurônio ``target``.

    As quatro entradas diagonais representam autorrecorrência e permanecem
    fixas em 0.7. As doze conexões não diagonais são potencialmente
    modificáveis.
    """

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
        """
        Saída pós-competição da iteração anterior.

        Como apenas um neurônio permanece ativo, normalmente somente uma
        posição do vetor é diferente de zero.
        """

        return tuple(self._previous_competitive_output)

    def reset(self) -> None:
        """Restaura estado e RNG; a mesma seed reproduz a mesma rede."""

        self._rng.seed(self.config.random_seed)
        self._weights = []
        for target in range(NEURON_COUNT):
            target_weights = []
            for source in range(NEURON_COUNT):
                if target == source:
                    weight = self.config.recurrent_weight
                else:
                    weight = self._rng.uniform(
                        self.config.initial_weight_min,
                        self.config.initial_weight_max,
                    )
                target_weights.append(weight)
            self._weights.append(target_weights)

        self._shifts = [self.config.initial_shift] * NEURON_COUNT

        # Na primeira iteração não existe atividade recorrente anterior. Como
        # os quatro neurônios têm o mesmo shift e recebem a mesma entrada
        # sensorial, o primeiro vencedor tende a ser definido pelo mecanismo de
        # desempate aleatório.
        self._previous_competitive_output = [0.0] * NEURON_COUNT
        self._step_index = 0

    def step(self, sensory: SensoryInput) -> NeuralStepResult:
        """
        Processa as consequências sensoriais da ação anterior e seleciona a
        ação que será executada na próxima janela motora.

        Ordem causal adotada:
        1. a ação anterior modifica o ambiente;
        2. os sensores medem essa consequência;
        3. a rede combina o estímulo atual com sua atividade recorrente;
        4. um neurônio vence a competição;
        5. pesos e shifts são atualizados;
        6. o vencedor determina a próxima ação.

        A publicação não descreve completamente a ordem computacional das
        atualizações; esta sequência é uma hipótese operacional.
        """

        weights_before = self.weights
        shifts_before = self.shifts
        previous_output = self.previous_competitive_output

        # 1. Integração da entrada sensorial com a recorrência da etapa anterior.
        activation = self._calculate_activations(
            sensory_total=sensory.total,
            previous_output=previous_output,
        )

        # 2. Conversão da ativação em saída contínua entre 0 e 1.
        raw_output = self._calculate_sigmoid_outputs(activation)

        # 3. Competição winner-take-all: somente um neurônio permanece ativo.
        winner = self._select_winner(raw_output)
        competitive_output = self._apply_competition(raw_output, winner)

        # Aprendizagem decorrente da transição anterior -> atual.
        self._update_synaptic_weights(
            activation=activation,
            previous_output=previous_output,
            current_winner=winner,
        )

        # Regulação da excitabilidade individual dos neurônios.
        self._update_intrinsic_shifts(competitive_output)
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

    def _calculate_activations(
        self,
        *,
        sensory_total: float,
        previous_output: tuple[float, ...],
    ) -> tuple[float, ...]:
        """Soma as entradas sensorial e recorrente de cada neurônio."""

        activations = []
        for target in range(NEURON_COUNT):
            recurrent_input = 0.0
            for source in range(NEURON_COUNT):
                recurrent_input += (
                    self._weights[target][source] * previous_output[source]
                )

            activations.append(sensory_total + recurrent_input)

        return tuple(activations)

    def _calculate_sigmoid_outputs(
        self,
        activation: tuple[float, ...],
    ) -> tuple[float, ...]:
        outputs = []
        for neuron in range(NEURON_COUNT):
            output = sigmoid_output(
                activation[neuron],
                self._shifts[neuron],
                self.config.sigmoid_gain,
            )
            outputs.append(output)
        return tuple(outputs)

    def _select_winner(self, raw_output: tuple[float, ...]) -> int:
        maximum = max(raw_output)

        # O artigo não define o desempate; a reconstrução sorteia entre os
        # máximos.
        tied = [
            index
            for index, output in enumerate(raw_output)
            if math.isclose(output, maximum, rel_tol=0.0, abs_tol=1e-15)
        ]
        return self._rng.choice(tied)

    def _apply_competition(
        self,
        raw_output: tuple[float, ...],
        winner: int,
    ) -> tuple[float, ...]:
        """Mantém a saída do vencedor e inativa os demais neurônios."""

        return tuple(
            output if neuron == winner else 0.0
            for neuron, output in enumerate(raw_output)
        )

    def _update_synaptic_weights(
        self,
        activation: tuple[float, ...],
        previous_output: tuple[float, ...],
        current_winner: int,
    ) -> None:
        # O artigo não torna inequívoco se a regra deve ser aplicada somente ao
        # vencedor atual ou a todos os neurônios pós-sinápticos.
        if self.config.plasticity_scope == PlasticityScope.WINNER_ONLY:
            targets_to_update = (current_winner,)
        else:
            targets_to_update = range(NEURON_COUNT)

        # Hipótese temporal adotada: a saída competitiva da iteração anterior
        # representa a atividade pré-sináptica que contribui para a atualização
        # atual.
        epsilon = self.config.synaptic_learning_rate
        for target in targets_to_update:
            for source in range(NEURON_COUNT):
                if target == source:
                    continue
                old_weight = self._weights[target][source]
                delta = grossberg_delta(
                    input_j=previous_output[source],
                    activation_i=activation[target],
                    weight_ij=old_weight,
                    epsilon=epsilon,
                )
                self._weights[target][source] = old_weight + delta

        # As quatro conexões autorrecorrentes são fixas no artigo.
        for neuron in range(NEURON_COUNT):
            self._weights[neuron][neuron] = self.config.recurrent_weight

    def _update_intrinsic_shifts(
        self,
        competitive_output: tuple[float, ...],
    ) -> None:
        """
        Atualiza a excitabilidade interna dos quatro neurônios.

        Hipótese operacional: utiliza-se a saída após a competição. Assim, o
        vencedor recebe sua saída sigmoidal e os perdedores recebem zero.
        """

        xi = self.config.intrinsic_learning_rate
        updated_shifts = []
        for neuron in range(NEURON_COUNT):
            shift = intrinsic_shift(
                previous_shift=self._shifts[neuron],
                output=competitive_output[neuron],
                xi=xi,
            )
            updated_shifts.append(shift)
        self._shifts = updated_shifts
