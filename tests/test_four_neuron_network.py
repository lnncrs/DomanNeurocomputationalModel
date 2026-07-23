import math

import pytest

from src.neural import (
    FourNeuronNetwork,
    NeuralConfig,
    PlasticityScope,
    SensoryInput,
    SensoryNormalization,
    grossberg_delta,
    intrinsic_shift,
    sigmoid_output,
)


def test_sigmoid_is_stable_and_centered_on_shift():
    assert sigmoid_output(0.5, 0.5) == pytest.approx(0.5)
    assert sigmoid_output(1_000.0, 0.0) == pytest.approx(1.0)
    assert sigmoid_output(-1_000.0, 0.0) == pytest.approx(0.0)


@pytest.mark.parametrize(
    ("input_j", "activation", "weight", "expected_sign"),
    [
        (0.0, 1.0, 0.5, 0),
        (0.7, 0.5, 0.5, 0),
        (0.7, 0.8, 0.5, 1),
        (0.7, 0.2, 0.5, -1),
    ],
)
def test_grossberg_rule_cases(input_j, activation, weight, expected_sign):
    delta = grossberg_delta(
        input_j=input_j,
        activation_i=activation,
        weight_ij=weight,
        epsilon=0.01,
    )
    sign = 0 if delta == 0 else int(math.copysign(1, delta))
    assert sign == expected_sign


def test_intrinsic_activity_moves_shift_toward_output():
    assert intrinsic_shift(previous_shift=0.5, output=0.9, xi=0.1) > 0.5
    assert intrinsic_shift(previous_shift=0.5, output=0.1, xi=0.1) < 0.5


def test_normalization_is_explicit_and_summed():
    normalization = SensoryNormalization(
        acceleration_offset=1.0,
        acceleration_scale=0.5,
        visual_scale=2.0,
        sound_scale=3.0,
    )
    result = normalization.normalize(SensoryInput(3.0, 0.25, 0.5))
    assert result.acceleration == pytest.approx(1.0)
    assert result.visual == pytest.approx(0.5)
    assert result.sound == pytest.approx(1.5)
    assert result.total == pytest.approx(3.0)


def test_exactly_one_competitive_output_is_nonzero():
    result = FourNeuronNetwork().step(SensoryInput(acceleration=0.1))
    assert sum(value != 0 for value in result.competitive_output) == 1
    assert result.raw_output[result.winner] == max(result.raw_output)


def test_neuron_with_unique_highest_output_wins():
    network = FourNeuronNetwork(NeuralConfig(random_seed=3))
    network.step(SensoryInput(acceleration=0.1))
    result = network.step(SensoryInput(acceleration=0.2))
    assert result.raw_output.count(max(result.raw_output)) == 1
    assert result.winner == max(range(4), key=result.raw_output.__getitem__)


def test_ties_do_not_always_favor_first_neuron():
    winners = {
        FourNeuronNetwork(NeuralConfig(random_seed=seed)).step(SensoryInput()).winner
        for seed in range(20)
    }
    assert len(winners) > 1


def test_same_seed_reproduces_every_step_exactly():
    first = FourNeuronNetwork(NeuralConfig(random_seed=42))
    second = FourNeuronNetwork(NeuralConfig(random_seed=42))
    inputs = [
        SensoryInput(),
        SensoryInput(acceleration=0.2),
        SensoryInput(sound=1.0),
        SensoryInput(acceleration=0.4, visual=0.1),
    ]
    assert [first.step(item) for item in inputs] == [
        second.step(item) for item in inputs
    ]


def test_reset_replays_the_seeded_sequence():
    network = FourNeuronNetwork(NeuralConfig(random_seed=8))
    inputs = [SensoryInput(acceleration=index / 10) for index in range(6)]
    original = [network.step(item) for item in inputs]
    network.reset()
    replay = [network.step(item) for item in inputs]
    assert replay == original


@pytest.mark.parametrize(
    "scope", [PlasticityScope.WINNER_ONLY, PlasticityScope.ALL_POSTSYNAPTIC]
)
def test_recurrent_diagonal_remains_exactly_fixed(scope):
    network = FourNeuronNetwork(NeuralConfig(random_seed=4, plasticity_scope=scope))
    for index in range(2_000):
        network.step(
            SensoryInput(
                acceleration=(index % 7) / 20,
                visual=(index % 3) / 20,
                sound=0.5 if index % 11 == 0 else 0.0,
            )
        )
    assert [network.weights[i][i] for i in range(4)] == [0.7] * 4


def test_winner_only_changes_at_most_one_off_diagonal_weight_after_bootstrap():
    network = FourNeuronNetwork(
        NeuralConfig(random_seed=2, plasticity_scope=PlasticityScope.WINNER_ONLY)
    )
    network.step(SensoryInput(acceleration=0.1))
    result = network.step(SensoryInput(acceleration=0.3))
    changed = [
        (i, j)
        for i in range(4)
        for j in range(4)
        if result.weights_before[i][j] != result.weights_after[i][j]
    ]
    assert len(changed) <= 1


def test_weights_used_for_activation_are_the_before_weights():
    network = FourNeuronNetwork(NeuralConfig(random_seed=7))
    network.step(SensoryInput(acceleration=0.2))
    result = network.step(SensoryInput(acceleration=0.4))
    expected = tuple(
        result.sensory.total
        + sum(
            result.weights_before[i][j] * result.previous_competitive_output[j]
            for j in range(4)
        )
        for i in range(4)
    )
    assert result.activation == pytest.approx(expected)


def test_module_has_no_webots_dependency():
    source = __import__("inspect").getsource(
        __import__("src.neural.four_neuron_network", fromlist=["dummy"])
    )
    assert "from controller import" not in source
    assert "import controller" not in source
