"""
Controlador manual para testes (sem aprendizado)
"""


class ManualController:
    """Controlador com comandos fixos para validação"""

    def __init__(self, interface):
        self.interface = interface

    def forward(self, speed: float = 1.0):
        """Move o robô para frente"""
        self.interface.set_motors(speed, speed)

    def turn_left(self, speed: float = 0.5):
        """Vira para esquerda"""
        self.interface.set_motors(-speed, speed)

    def turn_right(self, speed: float = 0.5):
        """Vira para direita"""
        self.interface.set_motors(speed, -speed)

    def stop(self):
        """Para o robô"""
        self.interface.set_motors(0.0, 0.0)
