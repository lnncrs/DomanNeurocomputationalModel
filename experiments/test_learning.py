"""
Script de teste do aprendizado (sem Webots - simulação simplificada)
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import numpy as np

from src.neural.network import DormanNetwork


class SimpleSimulation:
    """Simulação simples para testar aprendizado"""

    def __init__(self):
        self.position = 0.0
        self.velocity = 0.0
        self.angle = 0.2  # Inclinação do plano

    def step(self, left_motor: float, right_motor: float):
        """Simula física básica"""
        force = (left_motor + right_motor) / 2
        gravity = -np.sin(self.angle)

        self.velocity += (force + gravity) * 0.01
        self.velocity *= 0.95  # Atrito
        self.position += self.velocity * 0.01

        return self.position


def test_learning():
    """Testa aprendizado em simulação simplificada"""
    sim = SimpleSimulation()
    network = DormanNetwork(n_sensors=4, learning_rate=0.05)

    total_reward = 0.0
    prev_pos = 0.0

    for step in range(1000):
        # Sensores fictícios
        sensors = np.array([sim.position, sim.velocity, sim.angle, 1.0])

        # Forward pass
        outputs = network.forward(sensors)
        left, right = network.get_motor_commands()

        # Simula
        new_pos = sim.step(left, right)

        # Reward = progresso
        reward = (new_pos - prev_pos) * 100
        prev_pos = new_pos

        # Aprende
        network.update(reward)

        total_reward += reward

        if step % 100 == 0:
            print(
                f"Step {step}: Position={new_pos:.4f}, Avg Reward={total_reward/100:.4f}"
            )
            total_reward = 0.0


if __name__ == "__main__":
    print("Testando aprendizado...")
    test_learning()
