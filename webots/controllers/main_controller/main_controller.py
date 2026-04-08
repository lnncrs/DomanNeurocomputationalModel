"""
Main Webots controller - interface entre Webots e o algoritmo de aprendizado
"""

import os
import sys

# Adiciona o diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from controller import Robot

from control.learning_controller import LearningController
from interfaces.webots_interface import WebotsInterface


def main():
    # Inicializa o robô do Webots
    robot = Robot()
    timestep = int(robot.getBasicTimeStep())

    # Cria interface e controlador
    interface = WebotsInterface(robot, timestep)
    controller = LearningController(interface)

    # Loop principal
    while robot.step(timestep) != -1:
        controller.step()


if __name__ == "__main__":
    main()
