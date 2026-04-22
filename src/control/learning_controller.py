"""
Controlador com aprendizado
"""

# TODO Este código não está completo, está em fase de desenvolvimento.

# import numpy as np

# from src.neural.network import DormanNetwork


# class LearningController:
#     """Controlador que aprende a descer o plano inclinado até a base"""

#     def __init__(self, interface, learning_rate: float = 0.01):
#         self.interface = interface
#         n_sensors = interface.get_n_sensors()
#         self.network = DormanNetwork(n_sensors, learning_rate)

#         self.prev_position = 0.0
#         self.total_reward = 0.0
#         self.step_count = 0
#         self.target_position = -5.5  # Base da rampa (objetivo)

#     def compute_reward(self, current_position: float) -> float:
#         """Calcula reward baseado no progresso até a base da rampa"""
#         # Distância até o objetivo
#         distance_to_target = abs(current_position - self.target_position)
#         prev_distance = abs(self.prev_position - self.target_position)

#         # Recompensa por se aproximar do objetivo
#         progress = prev_distance - distance_to_target
#         self.prev_position = current_position

#         # Recompensa positiva por descer em direção à base
#         reward = progress * 10.0

#         # Bonus por chegar próximo ao objetivo
#         if distance_to_target < 0.5:
#             reward += 50.0

#         return reward

#     def step(self):
#         """Executa um passo de controle"""
#         # Lê sensores
#         sensors = self.interface.read_sensors()
#         position = self.interface.get_position()

#         # Calcula saída da rede
#         outputs = self.network.forward(sensors)
#         left_motor, right_motor = self.network.get_motor_commands()

#         # Aplica comandos aos motores
#         self.interface.set_motors(left_motor, right_motor)

#         # Calcula reward e atualiza rede
#         reward = self.compute_reward(position)
#         self.network.update(reward)

#         # Estatísticas
#         self.total_reward += reward
#         self.step_count += 1

#         if self.step_count % 100 == 0:
#             avg_reward = self.total_reward / 100
#             print(f"Step {self.step_count}, Avg Reward: {avg_reward:.4f}")
#             self.total_reward = 0.0
