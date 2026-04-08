"""
Rede neural com 4 neurônios (Dorman network)
"""

import numpy as np

from .neuron import Neuron


class DormanNetwork:
    """Rede neural com 4 neurônios e aprendizado por reforço"""

    def __init__(self, n_sensors: int, learning_rate: float = 0.01):
        self.neurons = [Neuron(n_sensors, learning_rate) for _ in range(4)]
        self.last_outputs = np.zeros(4)

    def forward(self, sensor_inputs: np.ndarray) -> np.ndarray:
        """Calcula saída da rede"""
        outputs = np.array([neuron.forward(sensor_inputs) for neuron in self.neurons])
        self.last_outputs = outputs
        return outputs

    def update(self, reward: float):
        """Atualiza todos os neurônios"""
        for neuron in self.neurons:
            neuron.update(reward)

    def get_motor_commands(self) -> tuple[float, float]:
        """Converte saídas em comandos dos motores

        Paper original:
        - Neurônio 0 (N1): motor esquerdo → frente (clockwise)
        - Neurônio 1 (N2): motor esquerdo → trás (anticlockwise)
        - Neurônio 2 (N3): motor direito → frente (clockwise)
        - Neurônio 3 (N4): motor direito → trás (anticlockwise)
        """
        # Motor esquerdo = N1(frente) - N2(trás)
        left_motor = self.last_outputs[0] - self.last_outputs[1]

        # Motor direito = N3(frente) - N4(trás)
        right_motor = self.last_outputs[2] - self.last_outputs[3]

        return left_motor, right_motor
