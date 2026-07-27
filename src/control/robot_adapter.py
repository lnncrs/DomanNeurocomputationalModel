"""Adaptador entre ações neurais abstratas e um robô de quatro rodas"""

from __future__ import annotations

from dataclasses import dataclass

from src.neural import MotorAction


@dataclass(frozen=True)
class FourWheelCommand:
    """Coleção simples do conjunto de rodas"""

    wheel1: float
    wheel2: float
    wheel3: float
    wheel4: float

    def as_tuple(self) -> tuple[float, float, float, float]:
        return self.wheel1, self.wheel2, self.wheel3, self.wheel4


@dataclass
class MotorActionMapper:
    """Agrupa motores por eixo transversal para aderência ao artigo"""

    speed: float = 1.0
    front_clockwise_sign: float = 1.0
    rear_clockwise_sign: float = 1.0

    def map(self, action: MotorAction) -> FourWheelCommand:
        front = self.speed * self.front_clockwise_sign
        rear = self.speed * self.rear_clockwise_sign
        if action == MotorAction.FRONT_CLOCKWISE:
            return FourWheelCommand(front, front, 0.0, 0.0)
        if action == MotorAction.FRONT_COUNTERCLOCKWISE:
            return FourWheelCommand(-front, -front, 0.0, 0.0)
        if action == MotorAction.REAR_CLOCKWISE:
            return FourWheelCommand(0.0, 0.0, rear, rear)
        if action == MotorAction.REAR_COUNTERCLOCKWISE:
            return FourWheelCommand(0.0, 0.0, -rear, -rear)
        raise KeyError(action)
