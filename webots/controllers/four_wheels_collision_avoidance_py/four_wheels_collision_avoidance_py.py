"""Controller Python baseline para o FourWheelRobot.

Esta primeira versão reproduz o comportamento do controller C
``four_wheels_collision_avoidance``. O nome do diretório é mantido como base
para a futura inclusão de controle manual por joystick.
"""

from controller import Robot


TIME_STEP = 64
FORWARD_SPEED = 10.0
TURN_LEFT_SPEED = 1.0
TURN_RIGHT_SPEED = -1.0
PROXIMITY_THRESHOLD = 950.0
AVOIDANCE_STEPS = 100

DISTANCE_SENSOR_NAMES = ("ds_left", "ds_right")
WHEEL_NAMES = ("wheel1", "wheel2", "wheel3", "wheel4")


def main() -> None:
    robot = Robot()

    distance_sensors = [
        robot.getDevice(name) for name in DISTANCE_SENSOR_NAMES
    ]
    for sensor in distance_sensors:
        sensor.enable(TIME_STEP)

    wheels = [robot.getDevice(name) for name in WHEEL_NAMES]
    for wheel in wheels:
        wheel.setPosition(float("inf"))
        wheel.setVelocity(0.0)

    avoidance_steps_remaining = 0

    while robot.step(TIME_STEP) != -1:
        left_speed = FORWARD_SPEED
        right_speed = FORWARD_SPEED

        if avoidance_steps_remaining > 0:
            avoidance_steps_remaining -= 1
            left_speed = TURN_LEFT_SPEED
            right_speed = TURN_RIGHT_SPEED
        else:
            sensor_values = [sensor.getValue() for sensor in distance_sensors]
            if any(value < PROXIMITY_THRESHOLD for value in sensor_values):
                avoidance_steps_remaining = AVOIDANCE_STEPS

        # Duas rodas físicas por comando lógico de lado.
        wheels[0].setVelocity(left_speed)
        wheels[1].setVelocity(right_speed)
        wheels[2].setVelocity(left_speed)
        wheels[3].setVelocity(right_speed)


if __name__ == "__main__":
    main()
