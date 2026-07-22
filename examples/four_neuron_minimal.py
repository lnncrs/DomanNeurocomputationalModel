"""Exemplo determinístico da rede e do protocolo, sem Webots."""

from src.experiments import ExperimentConfig, ExperimentRunner
from src.neural import FourNeuronNetwork, NeuralConfig


network = FourNeuronNetwork(NeuralConfig(random_seed=42))
runner = ExperimentRunner(
    network,
    ExperimentConfig(
        movement_duration_seconds=0.5,
        sound_intensity=1.0,
        downhill_sign=-1,
    ),
)

initial = runner.start()
print(f"ação inicial: {initial.action.name}")

# Consequências hipotéticas das ações anteriores. Deslocamento negativo foi
# configurado como descida; somente essas iterações recebem estímulo sonoro.
observations = [
    (-0.002, 0.10),
    (-0.012, 0.24),
    (0.008, 0.08),
    (-0.015, 0.31),
]

for displacement, acceleration in observations:
    result = runner.complete_iteration(
        displacement=displacement,
        acceleration=acceleration,
    )
    print(
        f"iteração={result.iteration} "
        f"ação={result.previous_action.name} "
        f"direção={result.direction.value} "
        f"maraca={result.rewarding_sound} "
        f"próxima={result.next_action.name}"
    )
