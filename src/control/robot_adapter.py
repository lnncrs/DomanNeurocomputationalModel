"""Fronteira entre ações neurais abstratas e um robô de quatro rodas."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from src.neural import MotorAction


@dataclass(frozen=True)
class FourWheelCommand:
    wheel1: float
    wheel2: float
    wheel3: float
    wheel4: float

    def as_tuple(self) -> tuple[float, float, float, float]:
        return self.wheel1, self.wheel2, self.wheel3, self.wheel4


@dataclass(frozen=True)
class MotorActionMapper:
    """Agrupa motores por eixo somente para as ações da rede do artigo."""

    speed: float = 1.0
    front_clockwise_sign: float = 1.0
    rear_clockwise_sign: float = 1.0

    def map(self, action: MotorAction) -> FourWheelCommand:
        front = self.speed * self.front_clockwise_sign
        rear = self.speed * self.rear_clockwise_sign
        commands = {
            MotorAction.FRONT_CLOCKWISE: FourWheelCommand(front, front, 0.0, 0.0),
            MotorAction.FRONT_COUNTERCLOCKWISE: FourWheelCommand(-front, -front, 0.0, 0.0),
            MotorAction.REAR_CLOCKWISE: FourWheelCommand(0.0, 0.0, rear, rear),
            MotorAction.REAR_COUNTERCLOCKWISE: FourWheelCommand(0.0, 0.0, -rear, -rear),
        }
        return commands[action]


class RobotAdapter(ABC):
    """Contrato mínimo a ser implementado pelo Webots ou hardware real."""

    @abstractmethod
    def apply(self, command: FourWheelCommand) -> None:
        """Aplica simultaneamente as quatro velocidades abstratas."""

    @abstractmethod
    def stop(self) -> None:
        """Interrompe os quatro motores ao final de uma ação."""
