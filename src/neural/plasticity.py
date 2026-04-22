"""
Regras de plasticidade sináptica
"""

# TODO Este código não está completo, está em fase de desenvolvimento.

# import numpy as np


# class HebbianPlasticity:
#     """Aprendizado Hebbiano: neurônios que disparam juntos se conectam"""

#     def __init__(self, learning_rate: float = 0.01):
#         self.learning_rate = learning_rate

#     def update_weights(
#         self, pre_activity: float, post_activity: float, weights: np.ndarray
#     ) -> np.ndarray:
#         """Atualiza pesos via regra hebbiana"""
#         delta_w = self.learning_rate * pre_activity * post_activity
#         return weights + delta_w


# class ReinforcementPlasticity:
#     """Plasticidade baseada em reforço"""

#     def __init__(self, learning_rate: float = 0.01):
#         self.learning_rate = learning_rate

#     def update_weights(
#         self, activity: np.ndarray, reward: float, weights: np.ndarray
#     ) -> np.ndarray:
#         """Atualiza pesos baseado em reward global"""
#         delta_w = self.learning_rate * reward * activity
#         return weights + delta_w
