"""Modelo neural independente do simulador"""

from .four_neuron_network import (
    FourNeuronNetwork,
    MotorAction,
    NeuralConfig,
    NeuralStepResult,
    PlasticityScope,
    SensoryInput,
    SensoryNormalization,
    grossberg_delta,
    intrinsic_shift,
    sigmoid_output,
)

__all__ = [
    "FourNeuronNetwork",
    "MotorAction",
    "NeuralConfig",
    "NeuralStepResult",
    "PlasticityScope",
    "SensoryInput",
    "SensoryNormalization",
    "grossberg_delta",
    "intrinsic_shift",
    "sigmoid_output",
]
