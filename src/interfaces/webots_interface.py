"""
Interface específica para Webots
"""

import numpy as np

from .base_interface import RobotInterface


class WebotsInterface(RobotInterface):
    """Implementação da interface para Webots"""

    def __init__(self, robot, timestep: int):
        self.robot = robot
        self.timestep = timestep

        # Inicializa sensores e motores (adapte conforme seu robô)
        self.sensors = []
        self.left_motor = None
        self.right_motor = None

        self._setup_devices()

    def _setup_devices(self):
        """Configura sensores e motores do Webots"""
        # Motores
        self.left_motor = self.robot.getDevice("left_motor")
        self.right_motor = self.robot.getDevice("right_motor")
        self.left_motor.setPosition(float("inf"))  # Modo velocidade
        self.right_motor.setPosition(float("inf"))
        self.left_motor.setVelocity(0.0)
        self.right_motor.setVelocity(0.0)

        # Sensores de proximidade (4 direções)
        self.proximity_sensors = [
            self.robot.getDevice("ps_front"),
            self.robot.getDevice("ps_back"),
            self.robot.getDevice("ps_left"),
            self.robot.getDevice("ps_right"),
        ]
        for sensor in self.proximity_sensors:
            sensor.enable(self.timestep)

        # Giroscópio (orientação angular)
        self.gyro = self.robot.getDevice("gyro")
        self.gyro.enable(self.timestep)

        # GPS (posição global)
        self.gps = self.robot.getDevice("gps")
        self.gps.enable(self.timestep)

        # Bússola (direção)
        self.compass = self.robot.getDevice("compass")
        self.compass.enable(self.timestep)

        self.MAX_SPEED = 6.28  # rad/s

    def read_sensors(self) -> np.ndarray:
        """Lê sensores do Webots"""
        # 4 sensores de proximidade
        proximity = np.array([sensor.getValue() for sensor in self.proximity_sensors])

        # Normaliza proximity (0-500 -> 0-1)
        proximity = proximity / 500.0

        # Giroscópio (velocidade angular no eixo Z)
        gyro_values = self.gyro.getValues()
        angular_velocity = gyro_values[2]  # Yaw

        # Bússola (direção para o objetivo)
        compass_values = self.compass.getValues()
        heading = np.arctan2(compass_values[0], compass_values[1])

        # Combina todos os sensores
        sensor_data = np.concatenate([proximity, [angular_velocity], [heading]])

        return sensor_data

    def set_motors(self, left: float, right: float):
        """Define velocidades dos motores"""
        # Clamp entre -1 e 1
        left = np.clip(left, -1.0, 1.0)
        right = np.clip(right, -1.0, 1.0)

        self.left_motor.setVelocity(left * self.MAX_SPEED)
        self.right_motor.setVelocity(right * self.MAX_SPEED)

    def get_position(self) -> float:
        """Retorna posição no eixo do plano inclinado (coordenada Y)"""
        gps_values = self.gps.getValues()
        return gps_values[1]  # Y é o eixo ao longo da rampa

    def get_n_sensors(self) -> int:
        """Retorna número de sensores"""
        return 6  # 4 proximity + 1 gyro + 1 compass
