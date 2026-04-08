"""
Interface base abstrata para simulação/hardware
"""

from abc import ABC, abstractmethod

import numpy as np


class RobotInterface(ABC):
    """Interface abstrata para controle do robô"""

    @abstractmethod
    def read_sensors(self) -> np.ndarray:
        """Lê valores dos sensores"""
        pass

    @abstractmethod
    def set_motors(self, left: float, right: float):
        """Define velocidades dos motores"""
        pass

    @abstractmethod
    def get_position(self) -> float:
        """Retorna posição atual do robô"""
        pass

    @abstractmethod
    def get_n_sensors(self) -> int:
        """Retorna número de sensores"""
        pass
